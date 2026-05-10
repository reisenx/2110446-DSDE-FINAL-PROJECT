import csv

from pathlib import Path
from tqdm import tqdm

from config.parser_config import ParserConfig
from config.path_config import PathConfig
from logs.logs import Logs
from utility.parser_utility import ParserUtility


class BadPartyInspector:
    """
    An inspector class to inspect invalid party names
    """

    def __init__(self) -> None:
        """
        Constructor method of the BadPartyInspector class
        """

        self.unique_party_name: set[str] = set()
        self.document: list[tuple[str, str]] = []

    def run(self) -> None:
        """
        Main method of the BadPartyInspector class
        """

        self.get_all_bad_party_names()
        self.get_bad_party_names_csv_report()

    def get_bad_party_names_csv_report(self) -> None:
        """
        Write a CSV report for unique invalid party names
        """

        # Write Logs
        Logs.write_logs(messages=["[OK] Begin writing invalid party names on CSV file"])
        Logs.write_report(message="[OK] Begin writing invalid party names on CSV file")

        # Sort the document by party name
        self.document.sort()

        # Write a CSV report
        with open(
            str(PathConfig.BAD_PARTY_NAMES_FILE_PATH),
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(("party_name", "filename"))

            for party_name, filename in self.document:
                csv_writer.writerow((party_name, filename))

        # Write Logs
        Logs.write_logs(messages=["[OK] Done writing invalid party names on CSV file"])
        Logs.write_report(message="[OK] Done writing invalid party names on CSV file")

    def get_all_bad_party_names(self) -> None:
        """
        Extract all unique bad party names from all markdown files.
        """

        # Write Logs
        Logs.write_logs(messages=["[OK] Begin inspecting invalid party names"])
        Logs.write_report(message="[OK] Begin inspecting invalid party names")

        # Create output path
        PathConfig.PARSER_FOLDER_PATH.mkdir(parents=True, exist_ok=True)
        PathConfig.PARSER_INSPECT_FOLDER_PATH.mkdir(parents=True, exist_ok=True)

        # Initialize pages counter
        n_success = 0

        # Process all markdown files
        all_files = list(PathConfig.MARKDOWN_PATH.rglob("*.md"))
        for file_path in tqdm(
            all_files,
            desc="Inspecting invalid party names",
            unit="file",
        ):
            is_success = self.get_bad_party_name(file_path)

            # Update counter
            n_success += int(is_success)

        # Write Logs
        n_skipped = len(all_files) - n_success
        Logs.write_logs(
            messages=[
                f"[OK] Done inspecting invalid party names on {n_success} markdown files",
                f"[SKIP] Skipped {n_skipped} markdown files",
            ]
        )
        Logs.write_report(
            message=f"[OK] Done inspecting invalid party names on {n_success} markdown files with {n_skipped} files skipped"
        )

    def get_bad_party_name(self, file_path: Path) -> bool:
        """
        Extract unique bad party names from a single markdown file

        Args:
            file_path (Path): markdown file path

        Returns:
            bool: True if extraction successful. Otherwise, False.
        """

        # Write Logs
        Logs.write_logs(
            messages=[
                f"[OK] Begin extracting invalid party names from {file_path.name}"
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

                    # Find party name column
                    party_name_column_idx = ParserUtility.get_party_name_column_idx(
                        table_cells
                    )

                    # Skip if the party column is not found
                    if party_name_column_idx == -1:
                        continue

                    # Get party name from the current row
                    party_name = table_cells[party_name_column_idx]
                    party_name = ParserConfig.REGEX_WHITESPACE.sub(
                        "", party_name
                    ).strip()

                    # Skip if the current party name is a table header cell or total score cell
                    if ParserUtility.is_header_cell(
                        party_name
                    ) or ParserUtility.is_total_score_cell(party_name):
                        continue

                    # Update object variables
                    if (
                        party_name not in self.unique_party_name
                        and ParserUtility.is_bad_party_name(party_name)
                    ):
                        self.unique_party_name.add(party_name)
                        self.document.append((party_name, file_path.name))

        # Write logs
        Logs.write_logs(
            messages=[f"[OK] Done extracting invalid party names from {file_path.name}"]
        )
        return True
