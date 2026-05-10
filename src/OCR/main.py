from logs.logs import Logs
from input.pdf_collector import PDFCollector
from input.jpg_converter import JPGConverter
from model.thai_ocr import ThaiOCR


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

        # Process the files
        Main.process_files()

    @staticmethod
    def setup_input_files():
        """
        Setup input flies by collecting PDF files then converting
        them to JPG images
        """

        PDFCollector.collect_all_pdf_files()
        JPGConverter.get_all_jpg_from_pdf_files()

    @staticmethod
    def process_files():
        """
        Perform OCR on image files then cleaning them
        """

        thai_ocr = ThaiOCR()
        thai_ocr.get_all_markdown_from_images()


if __name__ == "__main__":
    Main.main()
