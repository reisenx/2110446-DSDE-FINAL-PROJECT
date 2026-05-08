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
