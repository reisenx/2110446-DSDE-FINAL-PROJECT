from pathlib import Path


class PathConfig:
    """
    Path Configuration for the project. Every folder and file path
    on this application must be declared here.
    """

    # DEFINE RESOURCES PATHS
    ROOT_PATH: Path = Path(__file__).resolve().parent.parent.parent.parent
    RAW_DATASET_PATH: Path = ROOT_PATH / "data" / "raw"

    # DEFINE OUTPUT PATHS
    PDF_PATH: Path = ROOT_PATH / "data" / "pdf"
    JPG_PATH: Path = ROOT_PATH / "data" / "jpg"
    MARKDOWN_PATH: Path = ROOT_PATH / "generated" / "markdown"
    CSV_PATH: Path = ROOT_PATH / "generated" / "csv"

    # DEFINE LOGS PATHS
    LOG_FOLDER_PATH: Path = ROOT_PATH / "generated" / "logs"
    LOG_FILE_PATH: Path = LOG_FOLDER_PATH / "log.txt"
    REPORT_FILE_PATH: Path = LOG_FOLDER_PATH / "report.txt"

    # DEFINE PARSER PATHS
    PARSER_FOLDER_PATH: Path = ROOT_PATH / "generated" / "parser"

    PARSER_INSPECT_FOLDER_PATH: Path = PARSER_FOLDER_PATH / "inspection"
    PARSER_CSV_FOLDER_PATH: Path = PARSER_FOLDER_PATH / "csv"

    BAD_PARTY_NAMES_FILE_PATH: Path = PARSER_INSPECT_FOLDER_PATH / "bad_party_names.csv"
    BAD_NUMBER_TOKENS_FILE_PATH: Path = (
        PARSER_INSPECT_FOLDER_PATH / "bad_number_tokens.csv"
    )
    VOTE_RESULTS_FILE_PATH: Path = PARSER_INSPECT_FOLDER_PATH / "vote_results.csv"

    # DEFINE EXCEPTIONS
    EXCEPTION_FILENAMES: list[str] = ["desktop.ini"]
    OCR_EXCEPTION_FILENAMES: list[str] = [
        "district_mae_tha__02_subdistrict_municipality_tha_sop_chai__polling_unit_7__constituency_vote_page_2.jpg",
        "district_mueang_lamphun__01_subdistrict_ton_thong__polling_unit_1__constituency_vote_page_2.jpg",
        "district_mueang_lamphun__04_subdistrict_rim_ping__polling_unit_9__constituency_vote_page_2.jpg",
        "district_mueang_lamphun__09_subdistrict_si_bua_ban__polling_unit_3__party_list_vote_page_4.jpg",
        "district_mueang_lamphun__11_subdistrict_pa_sak__polling_unit_12__constituency_vote_page_2.jpg",
        "district_mueang_lamphun__11_subdistrict_pa_sak__polling_unit_20__party_list_vote_page_4.jpg",
        "district_mueang_lamphun__12_subdistrict_umong__polling_unit_7__party_list_vote_page_4.jpg",
    ]
