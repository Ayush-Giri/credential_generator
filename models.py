"""Data models for the credential generator."""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class FieldType(Enum):
    """Semantic types that a form field can be classified as."""

    FIRST_NAME = auto()
    LAST_NAME = auto()
    FULL_NAME = auto()
    EMAIL = auto()
    PHONE = auto()
    PASSWORD = auto()
    CONFIRM_PASSWORD = auto()
    USERNAME = auto()
    DATE_OF_BIRTH = auto()
    AGE = auto()
    GENDER = auto()
    ADDRESS = auto()
    STREET = auto()
    CITY = auto()
    STATE = auto()
    ZIP_CODE = auto()
    COUNTRY = auto()
    COMPANY = auto()
    JOB_TITLE = auto()
    WEBSITE = auto()
    SSN = auto()
    CREDIT_CARD = auto()
    CVV = auto()
    EXPIRY_DATE = auto()
    TEXT = auto()       # Generic text fallback
    NUMBER = auto()     # Generic number fallback
    SKIP = auto()       # Hidden, submit, csrf – ignore


@dataclass
class FormField:
    """Represents a raw HTML form field extracted from a webpage."""

    tag: str                              # input, select, textarea
    input_type: str = "text"              # HTML type attribute
    name: str = ""
    field_id: str = ""
    placeholder: str = ""
    label: str = ""
    required: bool = False
    options: list[str] = field(default_factory=list)  # For <select> dropdowns
    autocomplete: str = ""


@dataclass
class ClassifiedField:
    """A form field with its detected semantic type."""

    raw: FormField
    semantic_type: FieldType
    display_name: str = ""                # Human-friendly name for display

    def __post_init__(self):
        if not self.display_name:
            # Build a readable name from available info
            self.display_name = (
                self.raw.label
                or self.raw.placeholder
                or self.raw.name
                or self.raw.field_id
                or self.semantic_type.name.replace("_", " ").title()
            )
