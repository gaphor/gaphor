import re
import sys
from pathlib import Path

import babel.messages.pofile as pofile


def invalid(messages):
    placeholders = re.compile(r"{\w*}")
    html_entity = re.compile(r"&\w+;")

    for message in messages:
        if not message.string or message.fuzzy:
            continue

        if "%" in message.id:
            yield message, f"Old %-syntax used '{message.id}'"

        id_formats = placeholders.findall(message.id)
        str_formats = placeholders.findall(message.string)

        if "{}" in id_formats:
            yield message, f"Empty placeholder for '{message.id}': '{message.string}'"

        if set(id_formats) != set(str_formats):
            yield (
                message,
                f"Invalid placeholders for '{message.id}': '{message.string}'",
            )

        if html_entity.findall(message.string):
            yield message, f"Translation contains HTML entities: '{message.string}'"


def check_po_files():
    po_path: Path = Path(__file__).resolve().parent
    have_errors = False
    for path in (path for path in po_path.iterdir() if path.suffix == ".po"):
        with path.open(encoding="utf-8") as po:
            messages = pofile.read_po(po)

        for message, error in invalid(messages):
            have_errors = True
            print(f"{path.name}:{message.lineno}: {error}.")  # noqa: T201
    return have_errors


if __name__ == "__main__":
    sys.exit(check_po_files())
