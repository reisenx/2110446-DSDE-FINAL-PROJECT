from pathlib import Path
from tqdm import tqdm

from config.path_config import PathConfig
from output.station import Station
from output.subdistrict import Subdistrict
from utility.imputer_utility import ImputerUtility


class ImputerManager:
    def __init__(self) -> None:
        """
        Constructor method of ImputerManager
        """

        self.stations: list[Station] = []
        self.subdistricts: dict[str, Subdistrict] = {}

        self._load_all_stations()
        self._set_subdistricts()

    def _load_all_stations(self) -> None:
        """
        Load all parsed CSV file to a list of Station objects
        """

        # Load all station CSV files to a list
        all_files: list[Path] = list(PathConfig.PARSER_CSV_FOLDER_PATH.rglob("*.csv"))
        for input_path in tqdm(all_files, desc="Loading parsed CSV files", unit="file"):
            self.stations.append(Station(input_path))

    def _set_subdistricts(self) -> None:
        """
        Assign each Station object inside a list to a subdistrict dictionary
        """

        # Iterate each station in a list
        for station in self.stations:
            subdistrict_name: str = ImputerUtility.get_subdistrict_name(station)

            # Skip if the subdistrict name is invalid
            if not subdistrict_name:
                continue

            # Otherwise, add it to the subdistrict dict
            if subdistrict_name not in self.subdistricts:
                self.subdistricts[subdistrict_name] = Subdistrict(subdistrict_name)
            self.subdistricts[subdistrict_name].add_station(station)

    def run_impute_all(self) -> None:
        """
        Impute every subdistrict inside this ImputerManager object
        """

        for _, subdistrict in tqdm(
            self.subdistricts.items(), desc="Imputing all subdistricts", unit="file"
        ):
            subdistrict.run_impute_all()

    def export_to_csv_all(self) -> None:
        """
        Export all station inside this ImputerManager object as CSV files
        """

        PathConfig.CSV_PATH.mkdir(parents=True, exist_ok=True)
        for station in tqdm(self.stations, desc="Exporting as CSV files", unit="file"):
            station.export_to_csv()
