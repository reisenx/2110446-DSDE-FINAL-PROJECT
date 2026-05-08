from logs.logs import Logs
from input.pdf_collector import PDFCollector
from input.jpg_convertor import JPGConverter


class Main:
    @staticmethod
    def main():
        """
        Main Application
        """

        # Initialize logs files
        Logs.init_logs()

        # Setup input files
        Main.setup_input_files()

    @staticmethod
    def setup_input_files():
        """
        Setup input flies by collecting PDF files then converting
        them to JPG images
        """

        PDFCollector.collect_all_pdf_files()
        JPGConverter.get_all_jpg_from_pdf_file()


if __name__ == "__main__":
    Main.main()
