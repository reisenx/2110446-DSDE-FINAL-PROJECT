import re
from config.path_config import PathConfig
from config.thai_config import ThaiConfig
from pathlib import Path


class FilenameTranslator:
    @staticmethod
    def get_translated_file_path(filepath: Path) -> str:
        """
        Translates a full relative filepath into a flatten filename

        Args:
            filepath (Path): input file path

        Returns:
            str: flatten filepath
        """

        # Get relative path of a file
        relative_folder_path = filepath.parent.relative_to(PathConfig.RAW_DATASET_PATH)

        # Get folder name
        folder_names = []
        for folder in relative_folder_path.parts:
            if folder.lower() not in PathConfig.EXCEPTION_FILENAMES:
                folder_names.append(
                    FilenameTranslator.get_translated_folder_name(folder)
                )
        folder_name = "__".join(folder_names)

        # Get filename
        filename = FilenameTranslator.get_translated_filename(filepath.stem)

        # Get file extension
        file_extension = filepath.suffix.lower()

        # Return translated filepath
        return f"{folder_name}__{filename}{file_extension}"

    @staticmethod
    def get_translated_filename(filename: str) -> str:
        """
        Translate a Thai filename into English.

        Args:
            filename (str): an input filename

        Returns:
            str: a translated version of filename

        Example:
            Usage: get_translated_filename("ส.ส.5-16 ชุดที่ 9")
            Result: "constituency_vote_09"

            Usage: get_translated_filename("ส.ส.5-17(บช)-ชุดที่ 1")
            Result: "party_list_vote_01"
        """

        # Determine the voting type
        translated_filename = "constituency_vote"
        if ThaiConfig.PARTY_LIST_VOTE_FILENAME_KEYWORD in filename:
            translated_filename = "party_list_vote"

        # Determine the file number
        match = re.search(r"ชุดที่\s*(\d+)", filename)
        if match:
            set_number = int(match.group(1))
            translated_filename = f"{translated_filename}_{set_number:02d}"

        return translated_filename

    @staticmethod
    def get_cleaned_ascii_token(token: str) -> str:
        """
        Converts an input token from into lowercase string
        with underscore as delimiter.
        If a cleaned token is empty, returns "x" instead.

        Args:
            token (str): an input text part

        Returns:
            str: cleaned text part

        Example:
            Usage: get_cleaned_ascii_token("Hello World! (2024)")
            Result: "hello_world_2024"
        """

        # Convert a text to lowercase and remove trailing spaces
        token = token.lower().strip()

        # Replace all non-english and non-number characters with underscore
        token = re.sub(r"[^a-z0-9]+", "_", token)
        token = re.sub(r"_+", "_", token).strip("_")

        # Returns cleaned text
        if token:
            return token
        return "x"

    @staticmethod
    def get_translated_place(text: str) -> str:
        """
        Translate a Thai places inside a text into English.

        Args:
            text (str): an input text

        Returns:
            str: a translated version of text

        Example:
            Usage: get_cleaned_ascii_token("ตำบลบ้านธิ")
            Result: "ตำบลban_thi"
        """

        text = text.strip()
        for place_th, place_en in ThaiConfig.THAI_PLACE_MAP.items():
            text = text.replace(place_th, place_en)
        return text

    @staticmethod
    def get_translated_folder_name(folder_name: str) -> str:
        """
        Translate a Thai folder name into English.

        Args:
            folder_name (str): a folder name of the file

        Returns:
            str: a translated version of folder name

        Example:
            Usage: get_translated_folder_name("01.ตำบลบ้านธิ")
            Result: "01_district_ban_thi"

            Usage: get_translated_folder_name("ล่วงหน้าในเขต")
            Result: "advance_in_district"

            Usage: get_translated_folder_name("ตำบลบ้านธิ")
            Result: "district_ban_thi"
        """

        # Remove trailing spaces
        folder_name = folder_name.strip()

        # Handle numbered prefix
        match = re.match(r"^(\d{1,2})\.(.+)$", folder_name)
        if match:
            number, rest = match.group(1), match.group(2).strip()
            rest = FilenameTranslator.get_translated_folder_name(rest)
            return f"{number}_{rest}"

        # Handle exact string match
        if folder_name in ThaiConfig.THAI_COMPONENTS_MAP:
            return ThaiConfig.THAI_COMPONENTS_MAP[folder_name]

        # Handle string prefixes
        for prefix_th, prefix_en in ThaiConfig.THAI_COMPONENTS_MAP.items():
            # Extract body content after the prefix
            if folder_name.startswith(prefix_th):
                body = folder_name[len(prefix_th) :].strip()

                # Translate the place inside the body content
                body = FilenameTranslator.get_translated_place(body)

                # Clean the body content
                body = FilenameTranslator.get_cleaned_ascii_token(body)

                # Apply english prefix
                return f"{prefix_en}_{body}"

        # Handle other cases
        folder_name = FilenameTranslator.get_translated_place(folder_name)
        folder_name = FilenameTranslator.get_cleaned_ascii_token(folder_name)
        return folder_name
