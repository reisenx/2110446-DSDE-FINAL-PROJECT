import shutil

from pathlib import Path
from tqdm import tqdm

from config.path_config import PathConfig
from input.filename_translator import FilenameTranslator
from logs.logs import Logs


class PDFCollector:
    """
    A collector class that collect raw PDF dataset from the nested folder structure
    then renames it by it path and put them in a single output folder
    """

    @staticmethod
    def collect_all_pdf_files() -> None:
        """
        Fetch all files from a dataset root path, renames each file by its path
        and copy them to a single output folder.
        """

        # Create output path
        PathConfig.PDF_PATH.mkdir(parents=True, exist_ok=True)

        # Write Logs
        Logs.write_logs(messages=["[OK] Begin collecting PDF files"])
        Logs.write_report(message="[OK] Begin collecting PDF files")

        # Initialize file counter
        n_success = 0

        # Collect all PDF files
        all_files = list(PathConfig.RAW_DATASET_PATH.rglob("*.pdf"))
        for file_path in tqdm(all_files, desc="Collecting PDF files", unit="file"):
            is_success = PDFCollector.collect_pdf_file(file_path)
            n_success += int(is_success)

        # Write Logs
        n_skipped = len(all_files) - n_success
        Logs.write_logs(
            messages=[
                f"[OK] Done collecting {n_success} PDF files with {n_skipped} files skipped"
            ]
        )
        Logs.write_report(
            message=f"[OK] Done collecting {n_success} PDF files with {n_skipped} files skipped"
        )

    @staticmethod
    def collect_pdf_file(file_path: Path) -> bool:
        """
        Copy a PDF file from a folder and renames it using the translator.

        Args:
            file_path (Path): input file path

        Returns:
            bool: determine if the file collecting is successful
        """

        # Write logs
        Logs.write_logs(messages=[f"[OK] Begin renaming {file_path.name}"])

        # Skip a file which is not the PDF file
        if not file_path.is_file() or file_path.suffix.lower() != ".pdf":
            Logs.write_logs(
                messages=[
                    f"[SKIP] Skipped {file_path.name} because it is not a PDF file"
                ]
            )
            return False

        # Define output path
        filename = FilenameTranslator.get_translated_file_path(file_path)
        output_path = PathConfig.PDF_PATH / filename

        # Skip if file already exists
        if output_path.exists():
            Logs.write_logs(
                messages=[
                    f"[SKIP] Skipped {file_path.name} because {output_path.name} is already exist"
                ]
            )
            return False

        # Copy a PDF file and rename it
        shutil.copy2(file_path, output_path)

        # Write logs
        Logs.write_logs(
            messages=[f"[OK] Done renaming {file_path.name} to {output_path.name}"]
        )
        return True
