import csv

from pathlib import Path
from tqdm import tqdm

from config.parser_config import ParserConfig
from config.path_config import PathConfig
from logs.logs import Logs
from parser.parser_utility import ParserUtility


class BadNumberTokenInspector:
    """
    An inspector class to inspect invalid Thai number tokens
    """

    def __init__(self) -> None:
        """
        Constructor method of the BadNumberTokenInspector class
        """

        self.unique_number_token: set[str] = set()
        self.document: list[tuple[str, str]] = []

    def run(self) -> None:
        """
        Main method of the BadNumberTokenInspector class
        """

        self.get_all_bad_number_tokens()
        self.get_bad_number_tokens_csv_report()

    def get_bad_number_tokens_csv_report(self) -> None:
        """
        Write a CSV report for unique invalid Thai number tokens.
        """

        # Write Logs
        Logs.write_logs(
            messages=["[OK] Begin writing invalid Thai number tokens on CSV file"]
        )
        Logs.write_report(
            message="[OK] Begin writing invalid Thai number tokens on CSV file"
        )

        # Sort the document by token
        self.document.sort()

        # Write a CSV report
        with open(
            str(PathConfig.BAD_NUMBER_TOKENS_FILE_PATH),
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(("bad_token", "filename"))

            for bad_token, filename in self.document:
                csv_writer.writerow((bad_token, filename))

        # Write Logs
        Logs.write_logs(
            messages=["[OK] Done writing invalid Thai number tokens on CSV file"]
        )
        Logs.write_report(
            message="[OK] Done writing invalid Thai number tokens on CSV file"
        )

    def get_all_bad_number_tokens(self) -> None:
        """
        Extract all unique invalid Thai number token from all markdown files.
        """

        # Write Logs
        Logs.write_logs(messages=["[OK] Begin inspecting invalid Thai number tokens"])
        Logs.write_report(message="[OK] Begin inspecting invalid Thai number tokens")

        # Create output path
        PathConfig.PARSER_FOLDER_PATH.mkdir(parents=True, exist_ok=True)
        PathConfig.PARSER_INSPECT_FOLDER_PATH.mkdir(parents=True, exist_ok=True)

        # Initialize pages counter
        n_success = 0

        # Process all markdown files
        all_files = list(PathConfig.MARKDOWN_PATH.rglob("*.md"))
        for file_path in tqdm(
            all_files,
            desc="Inspecting invalid Thai number tokens",
            unit="file",
        ):
            is_success = self.get_bad_number_tokens(file_path)

            # Update counter
            n_success += int(is_success)

        # Write Logs
        n_skipped = len(all_files) - n_success
        Logs.write_logs(
            messages=[
                f"[OK] Done inspecting invalid Thai number tokens on {n_success} markdown files",
                f"[SKIP] Skipped {n_skipped} markdown files",
            ]
        )
        Logs.write_report(
            message=f"[OK] Done inspecting invalid Thai number tokens on {n_success} markdown files with {n_skipped} files skipped"
        )

    def get_bad_number_tokens(self, file_path: Path) -> bool:
        """
        Extract unique bad number token from a single markdown file

        Args:
            file_path (Path): markdown file path

        Returns:
            bool: True if extraction successful. Otherwise, False.
        """

        # Write Logs
        Logs.write_logs(
            messages=[
                f"[OK] Begin extracting invalid Thai number tokens from {file_path.name}"
            ]
        )

        # Skip if the file has no table
        if not ParserUtility.has_table(file_path):
            Logs.write_logs(
                messages=[f"[SKIP] Skipped {file_path.name} because it has no table"]
            )
            return False

        with open(str(file_path), "r", encoding="utf-8") as file:
            # Read markdown file
            content = file.read()

            # Iterate each table in a document
            for table in ParserConfig.REGEX_TABLE_HTML_TAG.findall(content):
                # Iterate each table row in a table
                for table_row in ParserConfig.REGEX_TABLE_ROW_HTML_TAG.findall(table):
                    # Get all table cells from the current table row
                    table_cells = [
                        ParserUtility.get_cleaned_text(cell)
                        for cell in ParserConfig.REGEX_TABLE_CELL_HTML_TAG.findall(
                            table_row
                        )
                    ]

                    # Skip if the current row has only 1 column
                    if len(table_cells) < 2:
                        continue

                    # Find the score column
                    score_column_idx = ParserUtility.get_arabic_score_column_idx(
                        table_cells
                    )
                    if score_column_idx == -1:
                        score_column_idx = ParserUtility.get_thai_score_column_idx(
                            table_cells
                        )

                    # Skip if the score column is not found or found at the first column
                    if score_column_idx <= 0:
                        continue

                    # Skip if the current cell text is a table header cell or a total score cell
                    if ParserUtility.is_header_cell(
                        table_cells[score_column_idx]
                    ) or ParserUtility.is_total_score_cell(
                        table_cells[score_column_idx]
                    ):
                        continue

                    # Get bad thai number token from a text
                    bad_tokens = ParserUtility.extract_bad_number_tokens(
                        table_cells[score_column_idx]
                    )

                    # Update object variables
                    for bad_token in bad_tokens:
                        if bad_token not in self.unique_number_token:
                            self.unique_number_token.add(bad_token)
                            self.document.append((bad_token, file_path.name))

        # Write logs
        Logs.write_logs(
            messages=[
                f"[OK] Done extracting invalid Thai number tokens from {file_path.name}"
            ]
        )
        return True
