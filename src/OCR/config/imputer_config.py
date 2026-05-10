from output.station_type import StationType


class ImputerConfig:
    """
    Imputer Configuration for data postprocessing
    """

    BASELINE_PARTY: str = "ประชาชน"

    MIN_BASELINE_PARTY_SCORE: int = 20
    MIN_EXPECTED_SCORE: int = 5

    TARGET_PARTY_THRESHOLDS: dict[str, float] = {
        "เพื่อไทย": 0.20,
        "ภูมิใจไทย": 0.30,
        "ประชาธิปัตย์": 0.30,
    }

    EXCEPTION_STATION_TYPES: list[StationType] = [
        StationType.ADVANCED,
        StationType.OTHERS,
    ]
