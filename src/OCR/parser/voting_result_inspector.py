import csv

from pathlib import Path
from tqdm import tqdm

from config.parser_config import ParserConfig
from config.path_config import PathConfig
from logs.logs import Logs
from parser.parser_utility import ParserUtility


class VotingResultInspector:
    """
    An inspector class to inspect voting results
    """

    def __init__(self) -> None:
        """
        Constructor method of the VotingResultInspector class
        """

        self.document: list[tuple[int, str, str, str]] = []

    def run(self) -> None:
        """
        Main method of the VotingResultInspector class
        """

        self.get_all_vote_results()
        self.get_vote_results_csv_report()

    def get_vote_results_csv_report(self) -> None:
        """
        Write a CSV report for all voting results
        """

        # Write Logs
        Logs.write_logs(
            messages=["[OK] Begin writing voting result listings on CSV file"]
        )
        Logs.write_report(
            message="[OK] Begin writing voting result listings on CSV file"
        )

        # Sort the document by token
        self.document.sort(reverse=True)

        # Write a CSV report
        with open(
            str(PathConfig.VOTE_RESULTS_FILE_PATH),
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(("arabic_vote", "thai_vote", "party_name", "filename"))

            for arabic_vote, thai_vote, party_name, filename in self.document:
                csv_writer.writerow((arabic_vote, thai_vote, party_name, filename))

        # Write Logs
        Logs.write_logs(
            messages=["[OK] Done writing voting result listings on CSV file"]
        )
        Logs.write_report(
            message="[OK] Done writing voting result listings on CSV file"
        )

    def get_all_vote_results(self) -> None:
        """
        Extract all Arabic and Thai vote results from all markdown files.
        """

        # Create output path
        PathConfig.PARSER_FOLDER_PATH.mkdir(parents=True, exist_ok=True)
        PathConfig.PARSER_INSPECT_FOLDER_PATH.mkdir(parents=True, exist_ok=True)

        # Write Logs
        Logs.write_logs(messages=["[OK] Begin inspecting voting results"])
        Logs.write_report(message="[OK] Begin inspecting voting results")

        # Initialize pages counter
        n_success = 0

        # Process all markdown files
        all_files = list(PathConfig.MARKDOWN_PATH.rglob("*.md"))
        for file_path in tqdm(
            all_files,
            desc="Inspecting voting results",
            unit="file",
        ):
            is_success = self.get_votes_result(file_path)

            # Update counter
            n_success += int(is_success)

        # Write Logs
        n_skipped = len(all_files) - n_success
        Logs.write_logs(
            messages=[
                f"[OK] Done inspecting voting results from {n_success} files with {n_skipped} files skipped"
            ]
        )
        Logs.write_report(
            message=f"[OK] Done inspecting voting results from {n_success} files with {n_skipped} files skipped"
        )

    def get_votes_result(self, file_path: Path) -> bool:
        """
        Extract all Arabic and Thai votes result from a single markdown file

        Args:
            file_path (Path): markdown file path

        Returns:
            bool: True if extraction successful. Otherwise, False.
        """

        # Write Logs
        Logs.write_logs(
            messages=[f"[OK] Begin extracting vote results from {file_path.name}"]
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

                    # Find the arabic score column
                    arabic_score_column_idx = ParserUtility.get_arabic_score_column_idx(
                        table_cells
                    )

                    # Find the Thai score column
                    thai_score_column_idx = ParserUtility.get_thai_score_column_idx(
                        table_cells
                    )

                    # Find party name column
                    party_name_column_idx = ParserUtility.get_party_name_column_idx(
                        table_cells
                    )

                    # Skip if the information is missing
                    if (
                        arabic_score_column_idx == -1 and thai_score_column_idx == -1
                    ) or (party_name_column_idx == -1):
                        continue

                    # Skip if the current cell text is a table header cell
                    if (
                        ParserUtility.is_header_cell(table_cells[thai_score_column_idx])
                        or ParserUtility.is_total_score_cell(
                            table_cells[thai_score_column_idx]
                        )
                        or ParserUtility.is_header_cell(
                            table_cells[party_name_column_idx]
                        )
                        or ParserUtility.is_total_score_cell(
                            table_cells[party_name_column_idx]
                        )
                    ):
                        continue

                    # Extract the information
                    arabic_vote = -1
                    if arabic_score_column_idx != -1:
                        arabic_vote = ParserUtility.extract_number_from_text(
                            table_cells[arabic_score_column_idx]
                        )

                    thai_vote = ""
                    if thai_score_column_idx != -1:
                        thai_vote = ParserUtility.extract_thai_from_text(
                            table_cells[thai_score_column_idx]
                        )

                    party_name = ""
                    if party_name_column_idx != -1:
                        party_name = ParserUtility.extract_thai_from_text(
                            table_cells[party_name_column_idx]
                        )

                    # Update object variables
                    self.document.append(
                        (arabic_vote, thai_vote, party_name, file_path.name)
                    )

        # Write logs
        Logs.write_logs(
            messages=[f"[OK] Done extracting vote results from {file_path.name}"]
        )
        return True
