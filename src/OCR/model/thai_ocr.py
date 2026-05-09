import os
import time
from dotenv import load_dotenv
from pathlib import Path
from collections import deque
from typhoon_ocr import ocr_document
from tqdm import tqdm
from logs.logs import Logs
from config.path_config import PathConfig


class ThaiOCR:
    def __init__(self):
        """
        Constructor method for ThaiOCR class
        """

        # Load Typhoon model API key
        load_dotenv()
        self.api_key = os.getenv("TYPHOON_API_KEY")

        # Model properties configuration
        self.model = "typhoon-ocr"
        self.figure_language = "Thai"
        self.task_type = "v1.5"

        # Image queue for OCR operations
        self.image_queue = deque()

        # Image queue configuration
        self.retry_delay = 2.0

    def load_image_queue(self) -> None:
        """
        Load all images into object's image queue
        """

        # Get a list of all image files
        all_files = list(PathConfig.JPG_PATH.rglob("*.jpg"))

        # Write logs
        Logs.write_logs(messages=["Starting Image Queue Loading Process"])
        Logs.write_report(message="Starting Image Queue Loading Process")

        # Initialize file counter
        n_success = 0

        # Iterate each image in a list
        for file_path in tqdm(all_files, desc="Load images to a queue", unit="file"):
            # Define the output path of an image
            output_path = ThaiOCR.get_output_path(file_path)

            # Skip all images that are in OCR file exception
            if file_path.name in PathConfig.OCR_EXCEPTION_FILENAMES:
                Logs.write_logs(
                    messages=[
                        f"Skipped {file_path.name} because it is in OCR file exception"
                    ]
                )
                continue

            # Skip all images that already converted.
            if output_path.exists():
                Logs.write_logs(
                    messages=[
                        f"Skipped {file_path.name} because {output_path.name} is already exist"
                    ]
                )
                continue

            # Add an image to a queue
            image_info = {"file_path": file_path, "n_attempts": 0}
            self.image_queue.append(image_info)

            # Update counter
            n_success += 1

        # Write logs
        n_skipped = len(all_files) - n_success
        Logs.write_logs(
            messages=[
                f"Done Image Queue Loading Process ({n_success} images loaded and {n_skipped} images skipped)"
            ]
        )
        Logs.write_report(
            message=f"Done Image Queue Loading Process ({n_success} images loaded and {n_skipped} images skipped)"
        )

    def get_all_markdown_from_images(self) -> None:
        """
        OCR all images from a folder then save each one as markdown file.
        """

        # Create the output directory
        PathConfig.MARKDOWN_PATH.mkdir(parents=True, exist_ok=True)

        # Load all images from a folder to the image queue
        self.load_image_queue()

        # Write logs
        Logs.write_logs(messages=["Starting Typhoon Model OCR Process"])
        Logs.write_report(message="Starting Typhoon Model OCR Process")

        # Initialize progress bar
        progress_bar = tqdm(
            total=len(self.image_queue), desc="Typhoon Model OCR Process"
        )

        # Process a queue until the model OCR all images
        while self.image_queue:
            # Pop the first image from the image queue
            image_info = self.image_queue.popleft()

            # Get the path information
            file_path = image_info["file_path"]
            output_path = ThaiOCR.get_output_path(file_path)

            # Process an image
            try:
                # Call a function to process an image
                self.get_markdown_from_image(file_path)

                # Update the progress bar
                progress_bar.update(1)

                # Write logs
                Logs.write_logs(
                    messages=[
                        f"Trying to OCR an image from path {file_path.name}",
                        f"Successfully OCR an image {file_path.name}",
                        f"Saved the result at {output_path.name}",
                    ]
                )

            except Exception as e:
                # Put the failed image back to the image queue
                image_info["n_attempts"] += 1
                self.image_queue.append(image_info)

                # Write logs
                n_attempts = image_info["n_attempts"]
                Logs.write_logs(
                    messages=[
                        f"Trying to OCR an image from path {file_path.name}",
                        f"Failed to OCR an image {file_path.name} ({n_attempts} attempts)",
                        f"Exception: {e}",
                        "Put the image back to the image queue",
                    ]
                )

                # Add delay before moving to the next image
                time.sleep(self.retry_delay)

        # Write logs
        Logs.write_logs(
            messages=[
                f"Done Typhoon Model OCR Process ({len(self.image_queue)} images processed)"
            ]
        )
        Logs.write_report(
            message=f"Done Typhoon Model OCR Process ({len(self.image_queue)} images processed)"
        )

    def get_markdown_from_image(self, file_path: Path) -> None:
        """
        OCR a single image and write the result as a markdown file

        Args:
            file_path (Path): image file path
        """

        # Define output path for the current image
        output_path = ThaiOCR.get_output_path(file_path)

        # Call Typhoon OCR model via API key
        document = ocr_document(
            str(file_path),
            model=self.model,
            figure_language=self.figure_language,
            task_type=self.task_type,
        )

        # Write OCR result as a markdown document
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(document.strip())

    @staticmethod
    def get_output_path(file_path: Path) -> Path:
        """
        Construct a output path from the input file path

        Args:
            file_path (Path): input file path

        Returns:
            Path: output file path
        """

        filename = f"{file_path.stem}.md"

        return PathConfig.MARKDOWN_PATH / filename
