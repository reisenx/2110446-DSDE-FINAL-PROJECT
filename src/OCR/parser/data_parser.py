import csv

from pathlib import Path
from tqdm import tqdm

from config.path_config import PathConfig
from config.parser_config import ParserConfig
from logs.logs import Logs
from parser.parser_utility import ParserUtility


class DataParser:
    """
    Parser class to prase an OCR markdown document to station voting result as CSV files
    """

    def __init__(self):
        """
        Constructor method of DataParser class
        """

        self.paths: dict[str, list[Path]] = self._build_paths_dict()

    def _build_paths_dict(self) -> dict[str, list[Path]]:
        """
        Build a path dictionary that groups markdown pages
        into a correspond CSV file

        Returns:
            dict[str, list[Path]]: indicates file grouping
        """

        # Write Logs
        Logs.write_logs(messages=["[OK] Begin building parsed CSV output paths"])
        Logs.write_report(message="[OK] Begin building parsed CSV output paths")

        # Initialize dictionary to group paths
        paths: dict[str, list[Path]] = {}

        # Create output path
        PathConfig.PARSER_CSV_FOLDER_PATH.mkdir(parents=True, exist_ok=True)

        # Iterate all markdown files
        all_files = list(PathConfig.MARKDOWN_PATH.rglob("*.md"))
        for input_path in tqdm(
            all_files,
            desc="Building parsed CSV output paths",
            unit="file",
        ):
            # Construct output CSV path
            prefix = input_path.name.split("_page_")[0]
            output_filename = f"{prefix}.csv"
            output_path = PathConfig.PARSER_CSV_FOLDER_PATH / output_filename

            # Update the each file path to a dictionary
            if str(output_path) not in paths:
                paths[str(output_path)] = []
            paths[str(output_path)].append(input_path)

        # Write Logs
        Logs.write_logs(
            messages=[
                f"[OK] Done building parsed CSV output paths from {len(all_files)} markdown files"
            ]
        )
        Logs.write_report(
            message=f"[OK] Done building parsed CSV output paths from {len(all_files)} markdown files"
        )

        return paths

    def get_all_csv_from_markdown_files(self):
        """
        Write all CSV final vote result reports
        """

        # Write Logs
        Logs.write_logs(
            messages=["[OK] Begin writing parsed voting results to CSV files"]
        )
        Logs.write_report(
            message="[OK] Begin writing parsed voting results to CSV files"
        )

        # Process each CSV file
        for output_path, input_paths in tqdm(
            self.paths.items(),
            desc="Writing parsed voting results to CSV files",
            unit="file",
        ):
            self.get_csv_from_markdown_files(input_paths, output_path)

        # Write Logs
        Logs.write_logs(
            messages=["[OK] Done writing parsed voting results to CSV files"]
        )
        Logs.write_report(
            message="[OK] Done writing parsed voting results to CSV files"
        )

    def get_csv_from_markdown_files(
        self, input_paths: list[Path], output_path: str
    ) -> None:
        """
        Count votes and write a single vote count CSV report

        Args:
            input_paths (list[Path]): list of markdown file paths for the current CSV file
            output_path (str): CSV file path
        """

        # Write Logs
        Logs.write_logs(
            messages=[f"[OK] Begin writing parsed voting results to {output_path}"]
        )

        # Determine voting type
        is_party_list_vote = ParserUtility.is_party_list_vote_file(output_path)

        # Initialize dict for vote counting
        votes = ParserUtility.init_constituency_votes_dict()
        if is_party_list_vote:
            votes = ParserUtility.init_party_list_votes_dict()

        # Iterate each markdown file
        for input_path in input_paths:
            # Get the vote result of current markdown file
            curr_votes = self.get_votes_from_markdown_file(input_path, output_path)

            # Update the voting dictionary
            for party_name, party_score in curr_votes.items():
                votes[party_name] += party_score

        # Write a CSV report
        with open(output_path, "w", encoding="utf-8-sig", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(("party", "score"))

            for party_name, party_score in votes.items():
                csv_writer.writerow((party_name, party_score))

        # Write Logs
        Logs.write_logs(
            messages=[f"[OK] Done writing parsed voting results to {output_path}"]
        )

    def get_votes_from_markdown_file(
        self, input_path: Path, output_path: str
    ) -> dict[str, int]:
        """
        Count votes from a single markdown file

        Args:
            input_path (Path): markdown file path
            output_path (str): CSV file path

        Returns:
            dict[str, int]: vote results for the markdown file.
        """

        # Write logs
        Logs.write_logs(
            messages=[f"[OK] Begin parsing voting results from {input_path.name}"]
        )

        # Determine voting type
        is_party_list_vote = ParserUtility.is_party_list_vote_file(output_path)

        # Initialize dict for vote counting
        votes = ParserUtility.init_constituency_votes_dict()
        if is_party_list_vote:
            votes = ParserUtility.init_party_list_votes_dict()

        # Skip if the file has no table
        if not ParserUtility.has_table(input_path):
            Logs.write_logs(
                messages=[f"[SKIP] Skipped {input_path.name} because it has no table"]
            )
            return votes

        # Open markdown file
        with open(input_path, "r", encoding="utf-8") as file:
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

                    # Fix the information
                    thai_vote = ParserUtility.get_fixed_thai_number(thai_vote)
                    party_name = ParserUtility.get_fixed_party_name(party_name)

                    # Skip if the party name is not in a vote count dict
                    if party_name not in votes:
                        continue

                    # Determine a vote score
                    final_score = ParserUtility.get_final_vote_score(
                        arabic_vote, thai_vote, party_name, is_party_list_vote
                    )

                    # Update the vote count dictionary
                    votes[party_name] += final_score

        # Write logs
        Logs.write_logs(
            messages=[f"[OK] Done parsing voting results from {input_path.name}"]
        )
        return votes
