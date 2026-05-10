import time

from config.path_config import PathConfig


class Logs:
    """
    Utility functions for logging the process inside the OCR application.
    """

    @staticmethod
    def init_logs() -> None:
        """
        Initialize the logs and report file by creating or clearing it.
        """

        # Create log folder
        PathConfig.LOG_FOLDER_PATH.mkdir(parents=True, exist_ok=True)

        # Create or clear the logs file.
        with open(PathConfig.LOG_FILE_PATH, "w", encoding="utf-8") as log_file:
            log_file.write(f"{'='*34} PROGRAM LOGS FILE {'='*35}\n")
            log_file.write(f"LOGS INITIALIZED AT {Logs.get_time_str()}\n")
            log_file.write(f"{'='*88}\n\n")

        # Create or clear the report file.
        with open(PathConfig.REPORT_FILE_PATH, "w", encoding="utf-8") as report_file:
            report_file.write(f"{'='*33} PROGRAM REPORT FILE {'='*34}\n")
            report_file.write(f"REPORT INITIALIZED AT {Logs.get_time_str()}\n")
            report_file.write(f"{'='*88}\n\n")

    @staticmethod
    def end_logs() -> None:
        """
        End the logs file by appending an end message with a timestamp.
        """

        with open(PathConfig.LOG_FILE_PATH, "a", encoding="utf-8") as log_file:
            log_file.write(f"\n{'='*37} END OF LOGS {'='*38}\n")
            log_file.write(f"LOGS ENDED AT {Logs.get_time_str()}\n")
            log_file.write(f"{'='*88}\n")

        with open(PathConfig.REPORT_FILE_PATH, "a", encoding="utf-8") as report_file:
            report_file.write(f"\n{'='*36} END OF REPORT {'='*37}\n")
            report_file.write(f"REPORT ENDED AT {Logs.get_time_str()}\n")
            report_file.write(f"{'='*88}\n")

    @staticmethod
    def write_logs(messages: list[str]) -> None:
        """
        Write logs messages to the logs file with a timestamp.

        Args:
            messages (list[str]): The logs messages to write.
        """

        with open(PathConfig.LOG_FILE_PATH, "a", encoding="utf-8") as log_file:
            log_file.write(f"TIMESTAMP: [{Logs.get_time_str()}]\n")
            for message in messages:
                log_file.write(f"  - {message}\n")

    @staticmethod
    def write_report(message: str) -> None:
        """
        Write a report message to the report file.

        Args:
            message (str): The report message to write.
        """

        with open(PathConfig.REPORT_FILE_PATH, "a", encoding="utf-8") as report_file:
            report_file.write(f"TIMESTAMP: [{Logs.get_time_str()}]\n - {message}\n\n")

    @staticmethod
    def get_time_str() -> str:
        """
        Get the current time as a formatted string.

        Returns:
            str: The current time formatted as "DAY, DD MMM YYYY HH:MM:SS".
        """

        return time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
