import re

from django.core.exceptions import ValidationError


def validate_number(value):
    if not re.match(r"^\+998\d{9}$", value):
        raise ValidationError("Please enter a valid phone number (e.g. +998901234567)")
    return value


def normalize_phone(raw: str) -> str:
    """Return the phone number as +998XXXXXXXXX or raise ValueError."""
    digits = re.sub(r"\D", "", raw or "")
    if len(digits) == 9:
        digits = f"998{digits}"
    if not re.fullmatch(r"998\d{9}", digits):
        raise ValueError("Invalid phone number")
    return f"+{digits}"
