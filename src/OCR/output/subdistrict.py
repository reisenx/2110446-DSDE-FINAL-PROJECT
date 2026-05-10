import statistics

from config.imputer_config import ImputerConfig
from output.station import Station
from output.station import StationType
from utility.imputer_utility import ImputerUtility


class Subdistrict:
    def __init__(self, name: str) -> None:
        """
        Constructor method for Subdistrict class

        Args:
            name (str): subdistrict name
        """

        self.name: str = name

        self.party_list_stations: list[Station] = []
        self.constituency_stations: list[Station] = []
        self.others_stations: list[Station] = []

        self.party_list_median_ratio: dict[str, float] = {}
        self.constituency_median_ratio: dict[str, float] = {}

    def add_station(self, station: Station) -> None:
        """
        Append the station object to the a list categorized by
        the station's type.

        Args:
            station (Station): station inside this subdistrict
        """

        if station.station_type == StationType.PARTY_LIST:
            self.party_list_stations.append(station)
            return

        if station.station_type == StationType.CONSTITUENCY:
            self.constituency_stations.append(station)
            return

        self.others_stations.append(station)

    def set_median_ratio(self) -> None:
        """
        Set median party list and constituency median ratio for all target parties.
        """

        for target_party, _ in ImputerConfig.TARGET_PARTY_THRESHOLDS.items():
            all_party_list_ratio: list[float] = []
            all_constituency_ratio: list[float] = []

            for station in self.party_list_stations:
                all_party_list_ratio.append(
                    station.ratio_to_baseline_party[target_party]
                )

            for station in self.constituency_stations:
                all_constituency_ratio.append(
                    station.ratio_to_baseline_party[target_party]
                )

            self.party_list_median_ratio[target_party] = 0.0
            if len(all_party_list_ratio) > 0:
                self.party_list_median_ratio[target_party] = statistics.median(
                    all_party_list_ratio
                )

            self.constituency_median_ratio[target_party] = 0.0
            if len(all_constituency_ratio) > 0:
                self.constituency_median_ratio[target_party] = statistics.median(
                    all_constituency_ratio
                )

    def run_impute_all(self) -> None:
        """
        Impute every station inside this subdistrict.
        """

        # Set the median ratio
        self.set_median_ratio()

        # Impute all party list stations
        for station in self.party_list_stations:
            self.run_impute(station)

        # Impute all constituency stations
        for station in self.constituency_stations:
            self.run_impute(station)

    def run_impute(self, station: Station) -> None:
        """
        Impute a single station which is inside this subdistrict

        Args:
            station (Station): station object
        """

        baseline_party: str = ImputerConfig.BASELINE_PARTY
        baseline_party_score: int = station.vote_scores[baseline_party]

        # Iterate each target party to impute
        for (
            target_party,
            target_threshold,
        ) in ImputerConfig.TARGET_PARTY_THRESHOLDS.items():
            # Get the target party score
            target_party_score: int = station.vote_scores[target_party]

            # Get the correct median ratio by the station type
            target_median_ratio: float = 0.0
            if station.station_type == StationType.PARTY_LIST:
                target_median_ratio: float = self.party_list_median_ratio[target_party]
            elif station.station_type == StationType.CONSTITUENCY:
                target_median_ratio: float = self.constituency_median_ratio[
                    target_party
                ]

            # Calculate expected score
            expected_score: float = ImputerUtility.get_expected_score(
                baseline_party_score, target_median_ratio
            )

            # Perform imputation
            if ImputerUtility.is_impute(
                baseline_party_score,
                target_party_score,
                target_median_ratio,
                target_threshold,
            ):
                station.vote_scores[target_party] = expected_score
