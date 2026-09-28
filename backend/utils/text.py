import re
from html import escape


REPLACEMENTS = {
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2013": "-",
    "\u2014": "-",
    "\u2026": "...",
    "\u00a0": " ",
    "\u2022": "-",
    "\u25cf": "-",
}


def sanitize_text(text: str) -> str:

    if not text:
        return ""

    for old, new in REPLACEMENTS.items():
        text = text.replace(old, new)

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    cleaned = []

    for char in text:

        if char == "\n":
            cleaned.append(char)

        elif char == "\t":
            cleaned.append(char)

        elif ord(char) >= 32:
            cleaned.append(char)

    return "".join(cleaned).strip()


def html_preview(text: str) -> str:

    safe_text = escape(
        sanitize_text(text)
    )

    return safe_text.replace(
        "\n",
        "<br>"
    )