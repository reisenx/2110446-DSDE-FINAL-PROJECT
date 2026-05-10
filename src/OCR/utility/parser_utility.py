import difflib
import html

from pathlib import Path
from pythainlp.util import thaiword_to_num

from config.parser_config import ParserConfig
from config.score_config import ScoreConfig
from config.thai_config import ThaiConfig
from logs.logs import Logs


class ParserUtility:
    """
    An utility function for markdown document parsing operations
    """

    # Class Parameters
    CUTOFF_SCORE = 0.85

    @staticmethod
    def get_cleaned_text(text: str) -> str:
        """
        Replace and remove HTML tags and whitespaces from a text

        Args:
            text (str): input text

        Returns:
            str: cleaned text
        """

        # Replace line break HTML tags with whitespace
        text = ParserConfig.REGEX_LINE_BREAK_HTML_TAG.sub(" ", text)

        # Remove all HTML tags
        text = ParserConfig.REGEX_HTML_TAG.sub("", text)

        # Decode HTML entities
        text = html.unescape(text)

        # Replace all whitespaces with a single space
        text = ParserConfig.REGEX_WHITESPACE.sub(" ", text).strip()

        return text

    @staticmethod
    def is_start_with_number(text: str) -> bool:
        """
        Check if a text starts with number

        Args:
            text (str): input text

        Returns:
            bool: True if a text starts with number. Otherwise, False.
        """

        # Clean a text
        text = ParserUtility.get_cleaned_text(text)

        # Remove all noise characters
        text = ParserConfig.REGEX_NOISE_CHARS.sub("", text)

        # Convert thai number to arabic number
        text = text.translate(ParserConfig.TRANSLATOR_THAI_NUMERALS).strip()

        # Check if it starts with number
        return bool(ParserConfig.REGEX_START_WITH_NUMBER.match(text))

    @staticmethod
    def is_header_cell(text: str) -> bool:
        """
        Check if the text inside the table cell is a header

        Args:
            text (str): text inside a cell

        Returns:
            bool: True if a text is a header. Otherwise, False.
        """

        text = ParserUtility.get_cleaned_text(text)

        return any(
            keyword in text for keyword in ParserConfig.HEADER_KEYWORD_EXCEPTIONS
        )

    @staticmethod
    def is_total_score_cell(text: str) -> bool:
        """
        Check if the text inside the table cell is a total score

        Args:
            text (str): text inside a cell

        Returns:
            bool: True if a text is a total score. Otherwise, False.
        """

        text = ParserUtility.get_cleaned_text(text)

        return any(keyword in text for keyword in ParserConfig.TOTAL_KEYWORD_EXCEPTIONS)

    @staticmethod
    def is_bad_party_name(party_name: str) -> bool:
        """
        Check if the party name is misspelled.

        Args:
            party_name (str): input party name

        Returns:
            bool: True if the party name is misspelled. Otherwise, False
        """

        return party_name.strip() not in ThaiConfig.THAI_PARTY_NAMES

    @staticmethod
    def is_party_list_vote_file(file_path_str: str) -> bool:
        """
        Check if the current file path is for party list voting

        Args:
            file_path_str (str): input file path

        Returns:
            bool: True if it is party list voting file. Otherwise, False.
        """

        return "party_list_vote" in file_path_str

    @staticmethod
    def has_table(file_path: Path) -> bool:
        """
        Check if the current markdown file has a table element inside.

        Args:
            file_path (Path): markdown file path

        Returns:
            bool: True if the markdown file has table. Otherwise, False
        """

        with open(str(file_path), "r", encoding="utf-8") as file:
            content = file.read()
            return bool(ParserConfig.REGEX_TABLE_HTML_TAG.search(content))

    @staticmethod
    def has_thai_number_token(text: str) -> bool:
        """
        Check if the text inside the table cell has any thai number token

        Args:
            text (str): text inside a cell

        Returns:
            bool: True if a text has Thai number token. Otherwise, False.
        """

        text = ParserUtility.get_cleaned_text(text)

        return any(token in text for token in ThaiConfig.THAI_NUMBER_TOKENS)

    @staticmethod
    def extract_number_from_text(text: str) -> int:
        """
        Extract only a first number appears on a text

        Args:
            text (str): an input text

        Returns:
            int: Return a number inside a text. If none, return -1
        """

        # Clean a text
        text = ParserUtility.get_cleaned_text(text)

        # Remove all noise characters
        text = ParserConfig.REGEX_NOISE_CHARS.sub(" ", text)

        # Convert thai number to arabic number
        text = text.translate(ParserConfig.TRANSLATOR_THAI_NUMERALS).strip()

        # Return only the first number appears on a text
        match = ParserConfig.REGEX_START_WITH_NUMBER.search(text)
        if match:
            return int(match.group(0))

        return -1

    @staticmethod
    def extract_thai_from_text(text: str) -> str:
        """
        Extract a Thai string with no whitespaces and symbols from a text

        Args:
            text (str): input text

        Returns:
            text: Thai string with no whitespaces and symbols
        """

        # Clean a text
        text = ParserUtility.get_cleaned_text(text)

        # Remove all noise characters
        text = ParserConfig.REGEX_NOISE_CHARS.sub("", text)

        # Convert thai number to arabic number
        text = text.translate(ParserConfig.TRANSLATOR_THAI_NUMERALS)

        # Remove all number and whitespaces
        text = ParserConfig.REGEX_NUMBER.sub("", text)
        text = ParserConfig.REGEX_WHITESPACE.sub("", text)

        return text

    @staticmethod
    def extract_bad_number_tokens(text: str) -> list[str]:
        """
        Extract a token that is invalid inside a text

        Args:
            text (str): Thai text in score column

        Returns:
            list[str]: list of invalid tokens
        """

        # Extract Thai substring from a text
        text = ParserUtility.extract_thai_from_text(text)

        # Split a text into multiple chunks by Thai number tokens
        chunks = ParserConfig.REGEX_THAI_NUMBER_TOKENS.split(text)

        # Iterate and collect the chunks that are invalid
        bad_tokens = []
        for chunk in chunks:
            if len(chunk) > 0 and chunk not in ThaiConfig.THAI_NUMBER_TOKENS:
                bad_tokens.append(chunk)

        return bad_tokens

    @staticmethod
    def get_arabic_score_column_idx(table_cells: list[str]) -> int:
        """
        Get an index of the arabic score column in a single table row

        Args:
            table_cells (list[str]): all table cells in a row

        Returns:
            int: Index of the score column. If not found, returns -1
        """

        column_idx = -1
        for idx in range(len(table_cells) - 1, -1, -1):
            if ParserUtility.is_start_with_number(table_cells[idx]):
                column_idx = idx
                break

        return column_idx

    @staticmethod
    def get_thai_score_column_idx(table_cells: list[str]) -> int:
        """
        Get an index of the Thai score column in a single table row

        Args:
            table_cells (list[str]): all table cells in a row

        Returns:
            int: Index of the score column. If not found, returns -1
        """

        column_idx = -1
        for idx in range(len(table_cells) - 1, -1, -1):
            if ParserConfig.REGEX_INSIDE_PARENTHESES.search(
                table_cells[idx]
            ) or ParserUtility.has_thai_number_token(table_cells[idx]):
                column_idx = idx
                break

        return column_idx

    @staticmethod
    def get_party_name_column_idx(table_cells: list[str]) -> int:
        """
        Get an index of the party name in a single table row

        Args:
            table_cells (list[str]): all table cells in a row

        Returns:
            int: Index of the score column. If not found, returns -1
        """

        # Get the leftmost score index which is not -1
        arabic_score_idx = ParserUtility.get_arabic_score_column_idx(table_cells)
        thai_score_idx = ParserUtility.get_thai_score_column_idx(table_cells)

        if arabic_score_idx == -1 and thai_score_idx == -1:
            return -1

        leftmost_score_idx = min(
            [idx for idx in (arabic_score_idx, thai_score_idx) if idx != -1]
        )

        if leftmost_score_idx <= 0:
            return -1

        # Loop from the score column to the left until found a text
        for idx in range(leftmost_score_idx - 1, -1, -1):
            result = ParserUtility.extract_thai_from_text(table_cells[idx])
            if result != "":
                return idx

        return -1

    @staticmethod
    def get_fixed_party_name(text: str) -> str:
        """
        Fix the misspelled party name by using fuzzy matching algorithm
        and mappings from data inspection

        Args:
            text (str): input party name

        Returns:
            str: fixed party name
        """

        # Extract only Thai part from an input text
        text = ParserUtility.extract_thai_from_text(text)

        # If the party name is already correct
        if not ParserUtility.is_bad_party_name(text):
            return text

        # Use mappings from data inspection
        if text in ParserConfig.FIXER_PARTY_NAME:
            return ParserConfig.FIXER_PARTY_NAME[text]

        # Implement fuzzy match if the text is not in the mappings
        result = difflib.get_close_matches(
            word=text,
            possibilities=ThaiConfig.THAI_PARTY_NAMES,
            n=1,
            cutoff=ParserUtility.CUTOFF_SCORE,
        )

        # Return the closest fuzzy match
        if result:
            return result[0]

        # Return the same party, if cannot be fixed
        return text

    @staticmethod
    def get_fixed_thai_number(text: str) -> str:
        """
        Fix the misspelled Thai number by using regular expression

        Args:
            text (str): input Thai number

        Returns:
            str: fixed Thai number
        """

        # Extract only Thai part from an input text
        text = ParserUtility.extract_thai_from_text(text)

        # Implement fixer from config class
        for pattern, replacement in ParserConfig.FIXER_NUMBER_TOKEN:
            text = pattern.sub(replacement, text)

        # Remove all non-thai number elements
        text = "".join(ParserConfig.REGEX_THAI_NUMBER_TOKENS.findall(text))

        return text

    @staticmethod
    def get_num_from_thai(thai_vote: str) -> int:
        """
        Convert Thai word to an integer using PyThaiNLP

        Args:
            thai_vote (str): input Thai word

        Returns:
            int: An integer number for the input Thai word. If cannot parse, returns -1
        """

        num = -1
        try:
            num = thaiword_to_num(thai_vote)
        except Exception as e:
            Logs.write_logs(
                messages=[
                    f"[ERROR] PyThaiNLP cannot parse {thai_vote} to int with exception {e}"
                ]
            )
            pass

        return num

    @staticmethod
    def get_final_vote_score(
        arabic_vote: int, thai_vote: str, party_name: str, is_party_list_vote: bool
    ) -> int:
        """
        Calculates the final vote score from various sources

        Args:
            arabic_vote (int): Vote score in Arabic numeral system
            thai_vote (str): Vote score in Thai words
            party_name (str): Party name
            is_party_list_vote (bool): Indicates voting type

        Returns:
            int: The final vote score
        """

        # Get real mean score per station
        real_mean_score = ScoreConfig.PARTY_LIST_PER_STATION_VOTES[party_name]
        if not is_party_list_vote:
            real_mean_score = ScoreConfig.CONSTITUENCY_PER_STATION_VOTES[party_name]

        # Calculate maximum score cap
        max_score_cap = real_mean_score * ScoreConfig.SCORE_CAP_MULTIPLIER

        # Convert Thai word to an integer
        thai_vote_num = ParserUtility.get_num_from_thai(thai_vote)

        # If both arabic vote and Thai vote is invalid
        if arabic_vote == -1 and thai_vote_num == -1:
            return 0

        # If Thai vote score is valid and not exceed the maximum score cap
        if 0 <= thai_vote_num <= max_score_cap:
            return thai_vote_num

        # If arabic score is valid and not exceed the maximum score cap
        if 0 <= arabic_vote <= max_score_cap:
            return arabic_vote

        # Otherwise, return real mean score
        return real_mean_score

    @staticmethod
    def init_party_list_votes_dict() -> dict[str, int]:
        """
        Initialize a dict for party list vote counting

        Returns:
            dict[str, int]: vote counter dict
        """

        return {party_name: 0 for party_name in ThaiConfig.THAI_PARTY_NAMES}

    @staticmethod
    def init_constituency_votes_dict():
        """
        Initialize a dict for constituency vote counting

        Returns:
            dict[str, int]: vote counter dict
        """

        return {party_name: 0 for party_name in ThaiConfig.CONSTITUENCY_PARTY_NAMES}
