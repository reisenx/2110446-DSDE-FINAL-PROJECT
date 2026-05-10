from input.jpg_converter import JPGConverter
from input.pdf_collector import PDFCollector
from logs.logs import Logs
from model.thai_ocr import ThaiOCR
from output.imputer_manager import ImputerManager
from parser.bad_party_inspector import BadPartyInspector
from parser.bad_number_token_inspector import BadNumberTokenInspector
from parser.data_parser import DataParser
from parser.voting_result_inspector import VotingResultInspector


class Main:
    """
    Main class of OCR application for the Thailand Election 2026 in Lamphun
    """

    @staticmethod
    def main() -> None:
        """
        Main Application
        """

        # Initialize logs files
        Logs.init_logs()

        # Setup input files
        Main.setup_input_files()

        # Process the files
        Main.process_files()

        # Output the CSV files
        Main.output_files()

    @staticmethod
    def setup_input_files() -> None:
        """
        Setup input flies by collecting PDF files then converting
        them to JPG images
        """

        PDFCollector.collect_all_pdf_files()
        JPGConverter.get_all_jpg_from_pdf_files()

    @staticmethod
    def process_files() -> None:
        """
        Perform OCR on image files then parsing them
        """

        # Performing OCR
        ThaiOCR().get_all_markdown_from_images()

        # Inspect markdown documents
        BadPartyInspector().run()
        BadNumberTokenInspector().run()
        VotingResultInspector().run()

        # Parse markdown documents
        DataParser().get_all_csv_from_markdown_files()

    @staticmethod
    def output_files() -> None:
        """
        Perform data postprocessing then export them as CSV files
        """

        imputer_manager = ImputerManager()
        imputer_manager.run_impute_all()
        imputer_manager.export_to_csv_all()


if __name__ == "__main__":
    Main.main()
