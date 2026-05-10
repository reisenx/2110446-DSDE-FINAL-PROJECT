import os
import time

from collections import deque
from dotenv import load_dotenv
from pathlib import Path
from tqdm import tqdm
from typhoon_ocr import ocr_document

from config.path_config import PathConfig
from logs.logs import Logs


class ThaiOCR:
    """
    Model class to perform OCR on a JPG image file into a markdown document.
    This class calls Typhoon OCR model via API
    """

    def __init__(self) -> None:
        """
        Constructor method for ThaiOCR class
        """

        # Load Typhoon model API key
        load_dotenv()
        self.api_key: str = os.getenv("TYPHOON_API_KEY")

        # Model properties configuration
        self.model: str = "typhoon-ocr"
        self.figure_language: str = "Thai"
        self.task_type: str = "v1.5"

        # Image queue for OCR operations
        self.image_queue: deque = deque()
        self.n_total_images: int = 0

        # Image queue configuration
        self.retry_delay: float = 2.0
        self.n_max_attempts: int = 5

    def load_image_queue(self) -> None:
        """
        Load all images into object's image queue
        """

        # Write logs
        Logs.write_logs(messages=["[OK] Begin loading ThaiOCR image queue"])
        Logs.write_report(message="[OK] Begin loading ThaiOCR image queue")

        # Get a list of all image files
        all_files = list(PathConfig.JPG_PATH.rglob("*.jpg"))

        # Initialize file counter
        n_success = 0

        # Iterate each image in a list
        for file_path in tqdm(
            all_files, desc="Loading ThaiOCR image queue", unit="file"
        ):
            # Define the output path of an image
            output_path = ThaiOCR.get_output_path(file_path)

            # Skip all images that are in OCR file exception
            if file_path.name in PathConfig.OCR_EXCEPTION_FILENAMES:
                Logs.write_logs(
                    messages=[
                        f"[SKIP] Skipped {file_path.name} as it is defined in the file exception"
                    ]
                )
                continue

            # Skip all images that already converted.
            if output_path.exists():
                Logs.write_logs(
                    messages=[
                        f"[SKIP] Skipped {file_path.name} because {output_path.name} is already exist"
                    ]
                )
                continue

            # Add an image to a queue
            image_info = {"file_path": file_path, "n_attempts": 0}
            self.image_queue.append(image_info)

            # Update counter
            n_success += 1

        # Store total images in the object
        self.n_total_images = n_success

        # Write logs
        n_skipped = len(all_files) - n_success
        Logs.write_logs(
            messages=[
                f"[OK] Done loading {n_success} images to ThaiOCR image queue with {n_skipped} images skipped."
            ]
        )
        Logs.write_report(
            message=f"[OK] Done loading {n_success} images to ThaiOCR image queue with {n_skipped} images skipped."
        )

    def get_all_markdown_from_images(self) -> None:
        """
        Perform OCR all images from a folder then save each one as markdown file.
        """

        # Write logs
        Logs.write_logs(messages=["[OK] Begin performing OCR on images"])
        Logs.write_report(message="[OK] Begin performing OCR on images")

        # Create the output directory
        PathConfig.MARKDOWN_PATH.mkdir(parents=True, exist_ok=True)

        # Load all images from a folder to the image queue
        self.load_image_queue()

        # Initialize progress bar
        progress_bar = tqdm(
            total=len(self.image_queue), desc="Performing OCR on images", unit="file"
        )

        # Process a queue until the model OCR all images
        while self.image_queue:
            # Pop the first image from the image queue
            image_info = self.image_queue.popleft()

            # Get the path information
            file_path = image_info["file_path"]
            output_path = ThaiOCR.get_output_path(file_path)

            # Update the attempts counter
            image_info["n_attempts"] += 1
            n_attempts = image_info["n_attempts"]

            # Process an image
            try:
                # Call a function to process an image
                self.get_markdown_from_image(file_path)

                # Update the progress bar
                progress_bar.update(1)

                # Write logs
                Logs.write_logs(
                    messages=[
                        f"[OK] Try to perform OCR on {file_path.name} image ({n_attempts} attempts)",
                        f"[OK] Successfully OCR on {file_path.name} image",
                        f"[OK] Saved the result as {output_path.name}",
                    ]
                )

            except Exception as e:
                # Write logs
                n_attempts = image_info["n_attempts"]
                Logs.write_logs(
                    messages=[
                        f"[OK] Try to perform OCR on {file_path.name} image ({n_attempts} attempts)",
                        f"[ERROR] Failed to OCR on {file_path.name} image with exception {e}",
                    ]
                )

                # Put the image back to an image queue
                if n_attempts < self.n_max_attempts:
                    self.image_queue.append(image_info)
                    Logs.write_logs(
                        messages=[
                            f"[OK] Put {file_path.name} image back to the image queue",
                            f"[OK] Added {self.retry_delay} seconds delay",
                        ]
                    )

                    # Add delay before moving to the next image
                    time.sleep(self.retry_delay)

                # Skip the image if it reaches maximum attempts
                else:
                    # Update the progress bar
                    progress_bar.update(1)

                    Logs.write_logs(
                        messages=[
                            f"[SKIP] Skipped {file_path.name} because it reaches maximum attempts",
                        ]
                    )

        # Write logs
        Logs.write_logs(
            messages=[f"[OK] Done performing OCR on {self.n_total_images} images"]
        )
        Logs.write_report(
            message=f"[OK] Done performing OCR on {self.n_total_images} images"
        )

    def get_markdown_from_image(self, file_path: Path) -> None:
        """
        Perform OCR on a single image and save the result as a markdown file

        Args:
            file_path (Path): JPG image file path
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
