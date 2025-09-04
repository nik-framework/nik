import datetime
import json
import re
import secrets
import string
from typing import Any

_acronym_uppercase_re = re.compile(r"([A-Z\d]+)([A-Z][a-z])")
_lower_digit_uppercase_re = re.compile(r"([a-z\d])([A-Z])")
_separators_re = re.compile(r"[_\-\s]+")


def _generate_words(text: str) -> list[str]:
    """Internal helper to convert a string into a list of lowercase words."""

    processed_text = text.strip()

    if not processed_text:
        return []

    # HTTPRequest -> HTTP_Request
    processed_text = _acronym_uppercase_re.sub(r"\1_\2", processed_text)

    # camelCaseExample -> camel_case_example
    processed_text = _lower_digit_uppercase_re.sub(r"\1_\2", processed_text)

    processed_text = processed_text.replace("-", "_")
    processed_text = processed_text.replace(" ", "_")

    processed_text = _separators_re.sub("_", processed_text)

    words = [word for word in processed_text.lower().split("_") if word]
    return words


def snake_case(text: str) -> str:
    """
    Converts a string to snake_case.
    Example: "camelCaseExample" -> "camel_case_example"
    """
    words = _generate_words(text)
    return "_".join(words)


def camel_case(text: str) -> str:
    """
    Converts a string to camel_case.
    Example: "PascalCaseExample" -> "pascalCaseExample"
    """
    words = _generate_words(text)
    if not words:
        return ""
    return words[0] + "".join(word.capitalize() for word in words[1:])


def pascal_case(text: str) -> str:
    """
    Converts a string to PascalCase (also known as UpperCamelCase).
    Example: "snake_case_example" -> "SnakeCaseExample"
    """
    words = _generate_words(text)
    if not words:
        return ""
    return "".join(word.capitalize() for word in words)


def random_string(template: str, length: int = 8) -> str:
    """
    Generates a random string based on a template format using a
    cryptographically secure random generator.
    Replaces `{random}` with a random alphanumeric string of a given length.

    :param template: The string template. e.g. "anon_{random}@example.com"
    :param length: The length of the random string to generate.
    :return: The formatted string with a random component.
    """
    if "{random}" in template:
        chars = string.ascii_lowercase + string.digits
        random_part = "".join(secrets.choice(chars) for _ in range(length))
        return template.replace("{random}", random_part)
    return template


class ValueObjectJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if hasattr(o, "to_json") and callable(o.to_json):
            return o.to_json()

        if isinstance(o, datetime.datetime):
            return o.isoformat()

        return super().default(o)


def to_json(obj: Any, **kwargs: Any) -> str:
    kwargs.setdefault("cls", ValueObjectJSONEncoder)
    return json.dumps(obj, **kwargs)
