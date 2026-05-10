from config.imputer_config import ImputerConfig
from output.station import Station


class ImputerUtility:
    """
    An utility function for data postprocessing
    """

    @staticmethod
    def get_subdistrict_name(station: Station) -> str:
        """
        Get the subdistrict from the station object

        Args:
            station (Station): station object

        Returns:
            str: subdistrict where the station is in
        """

        # Consider only the general election
        if station.station_type in ImputerConfig.EXCEPTION_STATION_TYPES:
            return ""

        elements = station.file_path.stem.split("__")

        if len(elements) < 4:
            return ""

        return elements[1].strip()

    @staticmethod
    def get_expected_score(
        baseline_party_score: int, target_median_ratio: float
    ) -> float:
        """
        Calculates expected score of the target party

        Args:
            baseline_party_score (int): baseline party score
            target_median_ratio (float): target party median ratio inside the subdistrict

        Returns:
            float: expected score
        """

        return target_median_ratio * baseline_party_score

    @staticmethod
    def is_impute(
        baseline_party_score: int,
        target_party_score: int,
        target_median_ratio: float,
        target_threshold: float,
    ) -> bool:
        """
        Check if the current station requires imputation.
        This method uses rule-based conditions as configured
        inside the ImputerConfig class

        Args:
            baseline_party_score (int): baseline party score
            target_party_score (int): target party score
            target_median_ratio (float): target party median ratio inside the subdistrict
            target_threshold (float): target party threshold constants

        Returns:
            bool: determine that the current station requires imputation
        """

        expected_score: float = ImputerUtility.get_expected_score(
            baseline_party_score, target_median_ratio
        )
        threshold_score: float = target_threshold * expected_score

        return (
            baseline_party_score > ImputerConfig.MIN_BASELINE_PARTY_SCORE
            and expected_score >= ImputerConfig.MIN_EXPECTED_SCORE
            and target_party_score < threshold_score
            and target_threshold > 0.0
        )
