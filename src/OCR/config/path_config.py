from pathlib import Path


class PathConfig:
    # DEFINE RESOURCES PATHS
    ROOT_PATH = Path(__file__).resolve().parent.parent.parent.parent
    RAW_DATASET_PATH = ROOT_PATH / "data" / "raw"

    # DEFINE OUTPUT PATHS
    PDF_PATH = ROOT_PATH / "data" / "pdf"
    JPG_PATH = ROOT_PATH / "data" / "jpg"
    CSV_PATH = ROOT_PATH / "data" / "csv"
    MARKDOWN_PATH = ROOT_PATH / "data" / "markdown"

    # DEFINE LOGS PATHS
    LOG_FOLDER_PATH = ROOT_PATH / "data" / "logs"
    LOG_FILE_PATH = LOG_FOLDER_PATH / "log.txt"
    REPORT_FILE_PATH = LOG_FOLDER_PATH / "report.txt"

    # DEFINE EXCEPTIONS
    EXCEPTION_FILENAMES = ["desktop.ini"]
    OCR_EXCEPTION_FILENAMES = [
        "district_mae_tha__02_subdistrict_municipality_tha_sop_chai__polling_unit_7__constituency_vote_page_2.jpg",
        "district_mueang_lamphun__01_subdistrict_ton_thong__polling_unit_1__constituency_vote_page_2.jpg",
        "district_mueang_lamphun__04_subdistrict_rim_ping__polling_unit_9__constituency_vote_page_2.jpg",
        "district_mueang_lamphun__09_subdistrict_si_bua_ban__polling_unit_3__party_list_vote_page_4.jpg",
        "district_mueang_lamphun__11_subdistrict_pa_sak__polling_unit_12__constituency_vote_page_2.jpg",
        "district_mueang_lamphun__11_subdistrict_pa_sak__polling_unit_20__party_list_vote_page_4.jpg",
        "district_mueang_lamphun__12_subdistrict_umong__polling_unit_7__party_list_vote_page_4.jpg",
    ]
