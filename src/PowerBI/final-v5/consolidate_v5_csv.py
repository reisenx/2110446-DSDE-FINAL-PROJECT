"""
consolidate_v5_csv.py
=====================
Reads all CSV files from v5/final_csv/, parses their English filenames to
extract election metadata, and writes a single consolidated fact_votes_v5.csv.

No cleaning rules are applied — raw data only.

Columns in output:
  party, score, election_type, ballot_type, amphoe, tambon, source_file
"""

import pandas as pd
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(SCRIPT_DIR, "final_csv")
OUTPUT_CSV = os.path.join(SCRIPT_DIR, "fact_votes_v5.csv")

AMPHOE_MAP = {
    "ban_thi": "อำเภอบ้านธิ",
    "mae_tha": "อำเภอแม่ทา",
    "mueang_lamphun": "อำเภอเมืองลำพูน",
}


def parse_filename(fname):
    """Return (election_type, ballot_type, amphoe, tambon) from v5 English filename."""
    base = fname.replace(".csv", "")

    # ballot type
    is_party_list = "party_list_vote" in base
    ballot_type = "บัญชีรายชื่อ" if is_party_list else "แบ่งเขต"

    if base.startswith("advance_in_district"):
        return "ล่วงหน้าในเขต", ballot_type, "", ""

    if base.startswith("advance_outside_district_and_overseas"):
        return "ล่วงหน้านอกเขต", ballot_type, "", ""

    if base.startswith("district_"):
        # Pattern: district_{amphoe}__{tambon_key}__polling_unit_{N}__{ballot}_vote
        parts = base.split("__")
        amphoe_key = parts[0].replace("district_", "")
        amphoe = AMPHOE_MAP.get(amphoe_key, amphoe_key)
        tambon_raw = parts[1] if len(parts) > 1 else ""
        # strip leading digits + subdistrict/municipality keywords for display
        tambon = re.sub(r"^\d+_subdistrict_", "", tambon_raw)
        tambon = re.sub(r"^\d+_municipality_", "", tambon)
        tambon = re.sub(r"_?municipality_?", " ", tambon)
        tambon = tambon.replace("_", " ").strip().title()
        return "เลือกตั้งทั่วไป", ballot_type, amphoe, tambon

    return "", ballot_type, "", ""


def main():
    csv_files = sorted(f for f in os.listdir(INPUT_DIR) if f.endswith(".csv"))
    print(f"Found {len(csv_files)} CSV files in v5/final_csv/")

    frames = []
    errors = []

    for fname in csv_files:
        path = os.path.join(INPUT_DIR, fname)
        try:
            df = pd.read_csv(
                path,
                header=0,
                names=["party", "score"],
                encoding="utf-8-sig",
                dtype={"party": str, "score": str},
            )
            # drop header rows and blanks
            df = df[
                df["party"].notna()
                & (df["party"] != "")
                & ~df["party"].isin(["party", "ชื่อพรรค"])
            ].copy()
            df["score"] = (
                pd.to_numeric(df["score"], errors="coerce").fillna(0).astype(int)
            )

            election_type, ballot_type, amphoe, tambon = parse_filename(fname)
            df["election_type"] = election_type
            df["ballot_type"] = ballot_type
            df["amphoe"] = amphoe
            df["tambon"] = tambon
            df["source_file"] = fname

            frames.append(df)
        except Exception as e:
            errors.append((fname, str(e)))

    if errors:
        print(f"\n{len(errors)} file(s) with errors:")
        for f, e in errors:
            print(f"  {f}: {e}")

    if not frames:
        print("No data loaded — exiting.")
        return

    result = pd.concat(frames, ignore_index=True)[
        [
            "party",
            "score",
            "election_type",
            "ballot_type",
            "amphoe",
            "tambon",
            "source_file",
        ]
    ]
    result.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"\nWrote {len(result):,} rows → {OUTPUT_CSV}")

    # Quick summary
    gen = result[result["election_type"] == "เลือกตั้งทั่วไป"]
    print("\nTop 10 parties (general election, by total score):")
    print(
        gen.groupby("party")["score"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .to_string()
    )


if __name__ == "__main__":
    main()
