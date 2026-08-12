import re

from unstructured.cleaners.core import (
    clean,
    clean_non_ascii_chars,
    replace_unicode_quotes,
)


def unbold_text(text: str) -> str:
    bold_numbers = {
        "𝟬": "0",
        "𝟭": "1",
        "𝟮": "2",
        "𝟯": "3",
        "𝟰": "4",
        "𝟱": "5",
        "𝟲": "6",
        "𝟳": "7",
        "𝟴": "8",
        "𝟵": "9",
    }

    def convert_bold_char(match: re.Match) -> str:
        char = match.group(0)

        if char in bold_numbers:
            return bold_numbers[char]

        if "\U0001d5d4" <= char <= "\U0001d5ed":
            return chr(ord(char) - 0x1D5D4 + ord("A"))

        if "\U0001d5ee" <= char <= "\U0001d607":
            return chr(ord(char) - 0x1D5EE + ord("a"))

        return char

    bold_pattern = re.compile(
        r"[\U0001D5D4-\U0001D5ED\U0001D5EE-\U0001D607\U0001D7CE-\U0001D7FF]"
    )

    return bold_pattern.sub(convert_bold_char, text)


def unitalic_text(text: str) -> str:
    def convert_italic_char(match: re.Match) -> str:
        char = match.group(0)

        if "\U0001d608" <= char <= "\U0001d621":
            return chr(ord(char) - 0x1D608 + ord("A"))

        if "\U0001d622" <= char <= "\U0001d63b":
            return chr(ord(char) - 0x1D622 + ord("a"))

        return char

    italic_pattern = re.compile(r"[\U0001D608-\U0001D621\U0001D622-\U0001D63B]")

    return italic_pattern.sub(convert_italic_char, text)


def remove_emojis_and_symbols(text: str) -> str:
    emoji_and_symbol_pattern = re.compile(
        "["
        "\U0001f600-\U0001f64f"
        "\U0001f300-\U0001f5ff"
        "\U0001f680-\U0001f6ff"
        "\U0001f1e0-\U0001f1ff"
        "\U00002193"
        "\U000021b3"
        "\U00002192"
        "]+",
        flags=re.UNICODE,
    )

    return emoji_and_symbol_pattern.sub(" ", text)


def replace_urls_with_placeholder(text: str, placeholder: str = "[URL]") -> str:
    url_pattern = r"https?://\S+|www\.\S+"

    return re.sub(url_pattern, placeholder, text)


def clean_text(text_content: str | None) -> str:
    if text_content is None:
        return ""

    cleaned_text = unbold_text(text_content)
    cleaned_text = unitalic_text(cleaned_text)
    cleaned_text = remove_emojis_and_symbols(cleaned_text)
    cleaned_text = clean(cleaned_text)
    cleaned_text = replace_unicode_quotes(cleaned_text)
    cleaned_text = clean_non_ascii_chars(cleaned_text)
    cleaned_text = replace_urls_with_placeholder(cleaned_text)

    return cleaned_text
