import re


class ParserConfig:
    """
    Configuration on Parser related tasks. Focus on Regular Expression
    for string manipulation.
    """

    # REGEX CONSTANTS FOR FILENAME TRANSLATOR CLASS
    REGEX_DOCUMENT_NUMBER: re.Pattern[str] = re.compile(r"ชุดที่\s*(\d+)")
    REGEX_NON_ALPHABET_AND_NON_NUMBER: re.Pattern[str] = re.compile(r"[^a-z0-9]+")
    REGEX_MULTIPLE_UNDERSCORES: re.Pattern[str] = re.compile(r"_+")
    REGEX_NUMBERED_PREFIX: re.Pattern[str] = re.compile(r"^(\d{1,2})\.(.+)$")
    REGEX_PARTY_LIST_FILE_INDICATOR: re.Pattern[str] = re.compile(re.escape("(บช)"))

    # REGEX CONSTANTS FOR DATA INSPECTOR CLASS
    REGEX_HTML_TAG: re.Pattern[str] = re.compile(r"<[^>]+>")
    REGEX_LINE_BREAK_HTML_TAG: re.Pattern[str] = re.compile(r"<br\s*/?>", re.IGNORECASE)
    REGEX_TABLE_HTML_TAG: re.Pattern[str] = re.compile(
        r"<table[^>]*>.*?</table>", re.IGNORECASE | re.DOTALL
    )
    REGEX_TABLE_ROW_HTML_TAG: re.Pattern[str] = re.compile(
        r"<tr[^>]*>(.*?)</tr>", re.IGNORECASE | re.DOTALL
    )
    REGEX_TABLE_CELL_HTML_TAG: re.Pattern[str] = re.compile(
        r"<t[dh][^>]*>(.*?)</t[dh]>", re.IGNORECASE | re.DOTALL
    )
    REGEX_WHITESPACE: re.Pattern[str] = re.compile(r"\s+")
    REGEX_NUMBER: re.Pattern[str] = re.compile(r"\d+")
    REGEX_NON_NUMBER: re.Pattern[str] = re.compile(r"\D+")
    REGEX_START_WITH_NUMBER: re.Pattern[str] = re.compile(r"^\d+")
    REGEX_NOISE_CHARS: re.Pattern[str] = re.compile(
        r"[\s\(\)\[\]\{\}\.,/'\"|\\ๆฯ!%+=☐☑✓•*\-]+"
    )
    REGEX_INSIDE_PARENTHESES: re.Pattern[str] = re.compile(r"\((.*?)\)")
    REGEX_THAI_NUMBER_TOKENS: re.Pattern[str] = re.compile(
        "ศูนย์|หนึ่ง|หมื่น|ร้อย|ล้าน|เก้า|เจ็ด|เอ็ด|พัน|ยี่|สอง|สาม|สิบ|สี่|ห้า|แปด|แสน|หก"
    )

    # DEFINE TRANSLATOR
    TRANSLATOR_THAI_NUMERALS: dict[int, int] = str.maketrans("๐๑๒๓๔๕๖๗๘๙", "0123456789")

    # DEFINE EXCEPTIONS
    HEADER_KEYWORD_EXCEPTIONS: list[str] = [
        "หมายเลขประจำตัว",
        "หมายเลขของบัญชีรายชื่อ",
        "ผู้สมัคร",
        "ชื่อ" "สังกัด",
        "พรรคการเมือง",
        "ได้คะแนน",
        "ให้กรอกทั้งตัวเลขและตัวอักษร",
    ]
    TOTAL_KEYWORD_EXCEPTIONS: list[str] = ["รวมคะแนนทั้งสิ้น"]

    # FIXER CONSTANTS
    FIXER_PARTY_NAME: dict[str, str] = {
        "กรุงเทพมหานคร": "กรีน",
        "กลาธรรม": "กล้าธรรม",
        "กลาโหม": "กล้าธรรม",
        "กล้วยธรรม": "กล้าธรรม",
        "กล้ำธรรม": "กล้าธรรม",
        "ก้าวลิสรณ": "ก้าวอิสระ",
        "ก้าวลิสรระ": "ก้าวอิสระ",
        "ก้าวลิสรละ": "ก้าวอิสระ",
        "ก้าวลิสระ": "ก้าวอิสระ",
        "ก้าวลิ่วสระ": "ก้าวอิสระ",
        "คลองไทยสภาชาติ": "คลองไทย",
        "คลองไทยสาขาติ": "คลองไทย",
        "คล้าธรรม": "กล้าธรรม",
        "คล้ายธรรม": "กล้าธรรม",
        "ท้องที่ไทยใหม่": "ท้องที่ไทย",
        "ปรมาชน": "ประชาชน",
        "ประชาธิปัตย์ใหม่": "ประชาธิปไตยใหม่",
        "ประชาธิปโดยใหม่": "ประชาธิปไตยใหม่",
        "ประชาอำสาขาติ": "ประชาอาสาชาติ",
        "ประธาน": "ประชาชน",
        "พลวัด": "พลวัต",
        "พลวัตไทย": "พลวัต",
        "พลังรวมใหม่": "พลังธรรมใหม่",
        "พิวจัน": "ฟิวชัน",
        "พิวซัน": "ฟิวชัน",
        "พ้องพี่ไทย": "ท้องที่ไทย",
        "ฟิวชันใหม่": "ฟิวชัน",
        "ฟิวซัน": "ฟิวชัน",
        "วิชขันใหม่": "วิชชั่นใหม่",
        "วิชข์นใหม่": "วิชชั่นใหม่",
        "วิชชชนใหม่": "วิชชั่นใหม่",
        "วิชชันใหม่": "วิชชั่นใหม่",
        "วิชชินใหม่": "วิชชั่นใหม่",
        "วิชชิ่นใหม่": "วิชชั่นใหม่",
        "วิชช์ขันใหม่": "วิชชั่นใหม่",
        "วิชช์ขึ้นใหม่": "วิชชั่นใหม่",
        "วิชช์ชนใหม่": "วิชชั่นใหม่",
        "วิชช์ชั่นใหม่": "วิชชั่นใหม่",
        "วิชช์ชั้นใหม่": "วิชชั่นใหม่",
        "วิชช์นนท์ใหม่": "วิชชั่นใหม่",
        "วิชช์นิ่มใหม่": "วิชชั่นใหม่",
        "วิชช์นใหม่": "วิชชั่นใหม่",
        "วิชช์ใหม่": "วิชชั่นใหม่",
        "วิชัยขึ้นใหม่": "วิชชั่นใหม่",
        "วิชัยชนใหม่": "วิชชั่นใหม่",
        "วิชัยใหม่": "วิชชั่นใหม่",
        "วิชาชีพใหม่": "วิชชัน",
        "ห้องที่ไทย": "ท้องที่ไทย",
        "เพื่อไทยชาติ": "เพื่อไทย",
        "แผนกต่อธรรม": "แผ่นดินธรรม",
        "แม่นดินธรรม": "แผ่นดินธรรม",
        "ใหม่สปป.ลาว": "ใหม่",
        "ใหม่สุโขทัย": "ใหม่",
        "ไทยก้าวหน้านาแห่งประเทศไทย": "ไทยก้าวหน้า",
        "ไทยก้าวหน้าบางแห่งประเทศไทย": "ไทยก้าวหน้า",
        "ไทยชนะรวม": "ไทยชนะ",
        "ไทยทรัพยากร": "ไทยทรัพย์ทวี",
    }

    FIXER_NUMBER_TOKEN: list[re.Pattern[str], str] = [
        (re.compile(r"ศนย|ศูนย"), "ศูนย์"),
        (re.compile(r"หนง|หนึง"), "หนึ่ง"),
        (re.compile(r"เอด"), "เอ็ด"),
        (re.compile(r"ยสบ|ยีสบ|ยสิบ|ยี่สบ"), "ยี่สิบ"),
        (re.compile(r"หมน|หมืน"), "หมื่น"),
        (re.compile(r"ลาน"), "ล้าน"),
        (re.compile(r"รอย"), "ร้อย"),
        (re.compile(r"พน"), "พัน"),
        (re.compile(r"เจด"), "เจ็ด"),
        (re.compile(r"เกา"), "เก้า"),
        (re.compile(r"สบ"), "สิบ"),
        (re.compile(r"หา"), "ห้า"),
        (re.compile(r"สีบ"), "สิบ"),
        (re.compile(r"สี"), "สี่"),
        (re.compile(r"สร้อย"), "สี่ร้อย"),
        (re.compile(r"สพัน"), "สี่พัน"),
        (re.compile(r"สพัน"), "สี่พัน"),
        (re.compile(r"สหมื่น"), "สี่หมื่น"),
        (re.compile(r"สแสน"), "สี่แสน"),
        (re.compile(r"สล้าน"), "สี่ล้าน"),
        (re.compile(r"สสิบ"), "สี่สิบ"),
    ]
