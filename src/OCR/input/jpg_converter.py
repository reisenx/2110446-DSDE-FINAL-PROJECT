import pypdfium2

from pathlib import Path
from tqdm import tqdm

from config.path_config import PathConfig
from logs.logs import Logs


class JPGConverter:
    """
    A converter class that converts PDF files to multiple JPG page files.
    """

    # Converter parameters
    SCALE: float = 2.0
    QUALITY: int = 90
    COLOR_MODE: str = "RGB"
    FILE_EXTENSION: str = "JPEG"

    @staticmethod
    def get_all_jpg_from_pdf_files() -> None:
        """
        Converts all PDF files to JPG file
        """

        # Write Logs
        Logs.write_logs(messages=["[OK] Begin converting PDF to JPG files"])
        Logs.write_report(message="[OK] Begin converting PDF to JPG files")

        # Create output path
        PathConfig.JPG_PATH.mkdir(parents=True, exist_ok=True)

        # Initialize pages counter
        n_success = 0
        n_total = 0

        # Converts all PDf files into JPG files
        all_files = list(PathConfig.PDF_PATH.rglob("*.pdf"))
        for file_path in tqdm(
            all_files, desc="Converting PDF to JPG files", unit="file"
        ):
            n_curr_success, n_curr_total = JPGConverter.get_jpg_from_pdf_file(file_path)

            # Update counter
            n_success += n_curr_success
            n_total += n_curr_total

        # Write Logs
        n_skipped = n_total - n_success
        Logs.write_logs(
            messages=[
                f"[OK] Done converting PDF to {n_success} JPG files with {n_skipped} pages skipped"
            ]
        )
        Logs.write_report(
            message=f"[OK] Done converting PDF to {n_success} JPG files with {n_skipped} pages skipped"
        )

    @staticmethod
    def get_jpg_from_pdf_file(file_path: Path) -> tuple[int, int]:
        """
        Converts a single PDF file to JPG file

        Args:
            file_path (Path): PDF file path

        Returns:
            tuple[int, int]: amount of successfully converted pages and total pages
        """

        # Write logs
        Logs.write_logs(
            messages=[f"[OK] Begin converting {file_path.name} to a JPG file"]
        )

        # Construct a PDF file object
        pdf_file = pypdfium2.PdfDocument(str(file_path))

        # Get page count of the current PDF file
        n_pages = len(pdf_file)
        n_successful_pages = 0

        # Iterate each page in a PDF file
        for idx in range(n_pages):
            # Define output path of a current page
            filename = f"{file_path.stem}_page_{idx + 1}.jpg"
            output_path = PathConfig.JPG_PATH / filename

            # Skip if the current page is already exist
            if output_path.exists():
                Logs.write_logs(
                    messages=[
                        f"[SKIP] Skipped {file_path.name} because {output_path.name} is already exist."
                    ]
                )
                continue

            # Converts to JPG file
            page = pdf_file[idx]
            bitmap = page.render(scale=JPGConverter.SCALE)
            image = bitmap.to_pil().convert(JPGConverter.COLOR_MODE)
            image.save(
                output_path, JPGConverter.FILE_EXTENSION, quality=JPGConverter.QUALITY
            )

            # Update counter
            n_successful_pages += 1

            # Write logs
            Logs.write_logs(
                messages=[
                    f"[OK] Done converting {file_path.name} to {output_path.name}"
                ]
            )

        return (n_successful_pages, n_pages)
