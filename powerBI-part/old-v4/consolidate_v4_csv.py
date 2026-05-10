"""
consolidate_v4_csv.py
=====================
Reads all CSV files from v4/result_csv/ (same raw source as v3),
applies four OCR-anomaly cleaning rules, and writes:
  • fact_votes_v4.csv      – cleaned consolidated data
  • anomaly_log_v4.txt     – every removed row with explanation

Cleaning rules (election-day rows only)
---------------------------------------
Rule 1 – Numeric / junk party names
    Drop rows whose party name is entirely digits, Thai numerals, or punctuation.
    These are OCR artefacts (row totals / page numbers captured as party labels).

Rule 2 – Per-unit outlier removal  (iterative ratio-to-2nd  OR  absolute > 950)
    Two sub-rules, applied as a union:

    2a. Iterative ratio-to-2nd:
        Within each polling-unit file, find the maximum score.  If it exceeds
        the 2nd-highest score × 15 (floor 500), it is a district-level aggregate
        the OCR captured as a single row.  Remove it, then repeat until the file
        is clean.  The iterative pass handles files with cascading subtotals
        (e.g. tha_pla_duk unit 12: removes ประชาชน 36287 then ไทยก้าวใหม่ 1083).

    2b. Absolute cap > 950:
        Removes scores > 950 that the ratio test misses because multiple
        anomalous values exist in the same file (e.g. กล้าธรรม 5275 where the
        file also contains รวมใจไทย 550, making the ratio only 9.6×).
        The cap 950 is chosen to be safely above legitimate high scores:
        the real top-party constituency max is ประชาชน 902 (wiang_yong unit 4),
        and the real เพื่อไทย max is 909 (ban_paen unit 1).

Rule 3 – Uniform-value anomaly
    If 5+ parties in one file share the exact same score > 5, that value is a
    page total or sequence number the OCR repeated on every line.

Rule 4 – Minor-party absolute cap (> 100 for parties with global mean < 3)
    Very minor parties that average < 3 votes per unit province-wide should
    never legitimately reach 100 in any single unit.
"""

import pandas as pd
import os
import re

SCRIPT_DIR     = os.path.dirname(os.path.abspath(__file__))
RESULT_CSV_DIR = os.path.join(SCRIPT_DIR, "result_csv")
OUTPUT_CSV     = os.path.join(SCRIPT_DIR, "fact_votes_v4.csv")
ANOMALY_LOG    = os.path.join(SCRIPT_DIR, "anomaly_log_v4.txt")

AMPHOE_MAP = {
    "ban_thi": "อำเภอบ้านธิ",
    "mae_tha": "อำเภอแม่ทา",
    "mueang_lamphun": "อำเภอเมืองลำพูน",
}

_NUMERIC_RE = re.compile(r"^[\d\s\.\-\,๐-๙๑๒๓๔๕๖๗๘]+$")


def parse_filename(fname):
    base        = fname.replace(".csv", "")
    ballot_type = "บัญชีรายชื่อ" if "(บช)" in base else "แบ่งเขต"
    if base.startswith("advance_in_district"):
        return "ล่วงหน้าในเขต", ballot_type, "", ""
    if base.startswith("advance_outside_district_and_overseas"):
        return "ล่วงหน้านอกเขต", ballot_type, "", ""
    if base.startswith("district_"):
        parts      = base.split("__")
        amphoe_key = parts[0].replace("district_", "")
        amphoe     = AMPHOE_MAP.get(amphoe_key, amphoe_key)
        tambon_raw = parts[1] if len(parts) > 1 else ""
        tambon     = re.sub(r"^\d+_subdistrict_", "", tambon_raw)
        tambon     = re.sub(r"_?municipality_?", " ", tambon)
        tambon     = tambon.replace("_", " ").strip().title()
        return "เลือกตั้งทั่วไป", ballot_type, amphoe, tambon
    return "", ballot_type, "", ""


def main():
    csv_files = sorted(f for f in os.listdir(RESULT_CSV_DIR) if f.endswith(".csv"))
    print(f"Found {len(csv_files)} CSV files\n")

    frames, errors = [], []
    for fname in csv_files:
        election_type, ballot_type, amphoe, tambon = parse_filename(fname)
        try:
            df = pd.read_csv(
                os.path.join(RESULT_CSV_DIR, fname),
                header=0, names=["party", "score"],
                encoding="utf-8", dtype={"party": str, "score": str}
            )
            df = df[~df["party"].isin(["party", "ชื่อพรรค"])]
            df = df[df["party"].notna() & (df["party"] != "")]
            df["score"]         = pd.to_numeric(df["score"], errors="coerce").fillna(0).astype(int)
            df["election_type"] = election_type
            df["ballot_type"]   = ballot_type
            df["amphoe"]        = amphoe
            df["tambon"]        = tambon
            df["source_file"]   = fname
            frames.append(df)
        except Exception as exc:
            errors.append((fname, str(exc)))

    raw    = pd.concat(frames, ignore_index=True)
    is_gen = raw["election_type"] == "เลือกตั้งทั่วไป"

    # ── Rule 1 ────────────────────────────────────────────────────────────────
    R1 = raw["party"].apply(
        lambda p: bool(_NUMERIC_RE.fullmatch(p.strip())) if p else False
    )

    # ── Rule 2a: iterative ratio-to-2nd (×15, floor 500) ─────────────────────
    bad_ratio = set()
    for sf, grp in raw[is_gen & ~R1].groupby("source_file"):
        remaining = grp.copy()
        while len(remaining) >= 2:
            s = remaining["score"].sort_values(ascending=False)
            top, sec = s.iloc[0], s.iloc[1]
            if top > max(sec * 15, 500):
                bad_ratio.add(remaining["score"].idxmax())
                remaining = remaining.drop(remaining["score"].idxmax())
            else:
                break
    R2a = pd.Series(False, index=raw.index)
    R2a[list(bad_ratio)] = True

    # ── Rule 2b: absolute cap > 950 ───────────────────────────────────────────
    R2b = is_gen & ~R1 & ~R2a & (raw["score"] > 950)
    R2  = R2a | R2b

    # ── Rule 3: uniform-value anomaly ─────────────────────────────────────────
    gen_post12 = raw[is_gen & ~R1 & ~R2]
    file_bad   = {}
    for sf, grp in gen_post12.groupby("source_file"):
        vc  = grp.loc[grp["score"] > 5, "score"].value_counts()
        bad = set(vc[vc >= 5].index)
        if bad:
            file_bad[sf] = bad

    R3 = raw.apply(
        lambda r: (is_gen[r.name]
                   and r["source_file"] in file_bad
                   and r["score"] in file_bad[r["source_file"]]
                   and r["score"] > 5),
        axis=1
    )

    # ── Rule 4: minor-party cap ────────────────────────────────────────────────
    party_mean = (
        raw[is_gen & ~R1 & ~R2 & ~R3]
        .groupby("party")["score"].mean()
    )
    minor = set(party_mean[party_mean < 3].index)
    R4 = is_gen & ~R1 & ~R2 & ~R3 & raw["party"].isin(minor) & (raw["score"] > 100)

    # ── Combine ────────────────────────────────────────────────────────────────
    drop = R1 | R2 | R3 | R4
    rule_label = pd.Series("", index=raw.index)
    rule_label[R1]               = "R1-numeric_party"
    rule_label[R2a & ~R1]        = "R2a-ratio_outlier"
    rule_label[R2b & ~R1 & ~R2a] = "R2b-absolute_cap"
    rule_label[R3 & ~R1 & ~R2]  = "R3-uniform_value"
    rule_label[R4]               = "R4-minor_party_cap"

    anomalies = raw[drop].copy()
    anomalies["anomaly_rule"] = rule_label[drop]

    clean = raw[~drop][[
        "party", "score", "election_type", "ballot_type", "amphoe", "tambon", "source_file"
    ]].copy()
    clean.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    # ── Write anomaly log ─────────────────────────────────────────────────────
    with open(ANOMALY_LOG, "w", encoding="utf-8") as fh:
        fh.write("anomaly_log_v4.txt\n" + "=" * 70 + "\n")
        fh.write(f"Total anomalous rows   : {len(anomalies):,}\n")
        fh.write(f"Total votes removed    : {anomalies['score'].sum():,}\n\n")

        LABELS = {
            "R1-numeric_party":  "Rule 1  – Numeric/junk party name",
            "R2a-ratio_outlier": "Rule 2a – Iterative ratio-to-2nd outlier (×15, floor 500)",
            "R2b-absolute_cap":  "Rule 2b – Absolute cap > 950",
            "R3-uniform_value":  "Rule 3  – Uniform-value anomaly (5+ parties same score)",
            "R4-minor_party_cap":"Rule 4  – Minor-party absolute cap (mean<3, score>100)",
        }
        for rkey, rlabel in LABELS.items():
            sub = anomalies[anomalies["anomaly_rule"] == rkey]
            fh.write("─" * 70 + "\n")
            fh.write(f"{rlabel}\n")
            fh.write(f"  Rows: {len(sub):,}  |  Votes removed: {sub['score'].sum():,}\n\n")
            for sf, grp in sub.groupby("source_file"):
                fh.write(f"  {sf}\n")
                for _, r in grp.sort_values("score", ascending=False).iterrows():
                    fh.write(f"    {r['party']:<38} score={r['score']:>7,}\n")
            fh.write("\n")

        fh.write("─" * 70 + "\n")
        fh.write("All anomalous party name strings (Rule 1)\n")
        r1p = anomalies[anomalies["anomaly_rule"] == "R1-numeric_party"]\
                  .groupby("party")["score"].agg(["sum","count"])\
                  .sort_values("sum", ascending=False)
        for p, row in r1p.iterrows():
            fh.write(f"  '{p}'  (files={int(row['count'])}, total_votes={int(row['sum']):,})\n")

    # ── Console summary ────────────────────────────────────────────────────────
    print("─" * 60)
    print(f"Clean rows written      : {len(clean):,}")
    print(f"Anomalous rows removed  : {len(anomalies):,}  ({anomalies['score'].sum():,} votes)")
    print(f"Parse errors            : {len(errors)}")
    print(f"\nBreakdown by election_type × ballot_type:")
    print(clean.groupby(["election_type","ballot_type"])["score"].sum()
          .reset_index().to_string(index=False))
    print(f"\nTop 10 parties by total votes:")
    print(clean.groupby("party")["score"].sum()
          .sort_values(ascending=False).head(10).to_string())
    print(f"\nAnomalies by rule:")
    for rk, s in anomalies.groupby("anomaly_rule"):
        print(f"  {rk:<25} {len(s):>4} rows | {s['score'].sum():>8,} votes")


if __name__ == "__main__":
    main()
