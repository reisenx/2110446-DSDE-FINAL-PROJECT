import csv

from pathlib import Path

from config.path_config import PathConfig
from config.imputer_config import ImputerConfig
from logs.logs import Logs
from output.station_type import StationType


class Station:
    def __init__(self, file_path: Path) -> None:
        """
        Constructor method of Station class

        Args:
            file_path (Path): Input CSV file
        """

        self.file_path: Path = file_path
        self.station_type: StationType = self._get_station_type()

        self.vote_scores: dict[str, int] = self._get_vote_scores()
        self.total_votes: int = self._get_total_votes()

        self.ratio_to_baseline_party: dict[str, float] = (
            self._get_ratio_to_baseline_party()
        )

    def export_to_csv(self) -> None:
        """
        Export the imputed value as a CSV file.
        """

        # Write Logs
        output_path: Path = PathConfig.CSV_PATH / self.file_path.name
        Logs.write_logs(
            messages=[
                f"[OK] Begin writing imputed voting results to {output_path.name}"
            ]
        )

        # Write CSV file
        with open(output_path, "w", encoding="utf-8-sig", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(("party", "score"))

            for party_name, party_score in self.vote_scores.items():
                csv_writer.writerow((party_name, party_score))

        # Write Logs
        Logs.write_logs(
            messages=[f"[OK] Done writing imputed voting results to {output_path}"]
        )

    def _get_station_type(self) -> StationType:
        """
        Determine the station type by its filename

        Returns:
            StationType: station type
        """

        if "advance" in self.file_path.stem:
            return StationType.ADVANCED

        if "party_list" in self.file_path.stem:
            return StationType.PARTY_LIST

        if "constituency_vote" in self.file_path.stem:
            return StationType.CONSTITUENCY

        return StationType.OTHERS

    def _get_vote_scores(self) -> dict[str, int]:
        """
        Read a parsed CSV file and store the vote result as a dict

        Returns:
            dict[str, int]: vote result read from a CSV file
        """

        vote_scores: dict[str, int] = {}

        with open(self.file_path, "r", encoding="utf-8-sig") as csv_file:
            for row in csv.DictReader(csv_file):
                vote_scores[row["party"]] = int(row["score"])

        return vote_scores

    def _get_total_votes(self) -> int:
        """
        Calculate total votes inside this station

        Returns:
            int: total votes
        """

        total_votes: int = 0
        for _, score in self.vote_scores.items():
            total_votes += score

        return total_votes

    def _get_ratio_to_baseline_party(self) -> dict[str, float]:
        """
        Calculate ratio of target party to the baseline party for imputation

        Returns:
            dict[str, float]: ratio of all target parties
        """

        baseline_party: str = ImputerConfig.BASELINE_PARTY
        ratio_to_baseline_party: dict[str, float] = {}

        for target_party, _ in ImputerConfig.TARGET_PARTY_THRESHOLDS.items():
            ratio_to_baseline_party[target_party] = 0.0
            if self.vote_scores[baseline_party] > 0:
                ratio_to_baseline_party[target_party] = (
                    self.vote_scores[target_party] / self.vote_scores[baseline_party]
                )

        return ratio_to_baseline_party
