"""Generate fake credential data for classified form fields."""

import random
import string
from datetime import date

from faker import Faker

from models import ClassifiedField, FieldType


def generate_credentials(
    fields: list[ClassifiedField],
    locale: str = "en_US",
) -> dict[str, str]:
    """Generate a dict of ``{display_name: generated_value}`` for each field.

    Uses the Faker library with the given *locale* to produce realistic data.
    Password and confirm-password fields always get the same value.
    """
    fake = Faker(locale)
    results: dict[str, str] = {}

    # Pre-generate a single password so password + confirm password match
    password_value = _generate_password()

    for cf in fields:
        if cf.semantic_type == FieldType.SKIP:
            continue
        if cf.semantic_type == FieldType.PASSWORD:
            results[cf.display_name] = password_value
        elif cf.semantic_type == FieldType.CONFIRM_PASSWORD:
            results[cf.display_name] = password_value
        else:
            value = _generate_value(fake, cf)
            results[cf.display_name] = value

    return results


# ---------------------------------------------------------------------------
# Per-type generators
# ---------------------------------------------------------------------------

def _generate_value(fake: Faker, cf: ClassifiedField) -> str:
    """Dispatch to the correct Faker method based on semantic type."""
    ft = cf.semantic_type
    generators: dict[FieldType, callable] = {
        FieldType.FIRST_NAME: lambda: fake.first_name(),
        FieldType.LAST_NAME: lambda: fake.last_name(),
        FieldType.FULL_NAME: lambda: fake.name(),
        FieldType.EMAIL: lambda: fake.email(),
        FieldType.PHONE: lambda: fake.phone_number(),
        FieldType.PASSWORD: lambda: _generate_password(),
        FieldType.USERNAME: lambda: fake.user_name(),
        FieldType.DATE_OF_BIRTH: lambda: _generate_dob(fake),
        FieldType.AGE: lambda: str(random.randint(18, 65)),
        FieldType.GENDER: lambda: _pick_gender(cf),
        FieldType.ADDRESS: lambda: fake.address().replace("\n", ", "),
        FieldType.STREET: lambda: fake.street_address(),
        FieldType.CITY: lambda: fake.city(),
        FieldType.STATE: lambda: fake.state() if hasattr(fake, "state") else fake.city(),
        FieldType.ZIP_CODE: lambda: fake.zipcode() if hasattr(fake, "zipcode") else fake.postcode(),
        FieldType.COUNTRY: lambda: fake.country(),
        FieldType.COMPANY: lambda: fake.company(),
        FieldType.JOB_TITLE: lambda: fake.job(),
        FieldType.WEBSITE: lambda: fake.url(),
        FieldType.SSN: lambda: fake.ssn() if hasattr(fake, "ssn") else "000-00-0000",
        FieldType.CREDIT_CARD: lambda: fake.credit_card_number(),
        FieldType.CVV: lambda: fake.credit_card_security_code(),
        FieldType.EXPIRY_DATE: lambda: fake.credit_card_expire(),
        FieldType.TEXT: lambda: _generic_text(fake, cf),
        FieldType.NUMBER: lambda: str(random.randint(1, 100)),
    }

    gen = generators.get(ft)
    if gen:
        return gen()
    return fake.word()


def _generate_password(
    length: int = 16,
    use_special: bool = True,
) -> str:
    """Generate a strong random password."""
    chars = string.ascii_letters + string.digits
    if use_special:
        chars += "!@#$%^&*()-_=+"

    # Guarantee at least one of each required category
    pw = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
    ]
    if use_special:
        pw.append(random.choice("!@#$%^&*()-_=+"))

    pw.extend(random.choices(chars, k=length - len(pw)))
    random.shuffle(pw)
    return "".join(pw)


def _generate_dob(fake: Faker) -> str:
    """Generate a realistic date of birth (18–65 years old)."""
    dob: date = fake.date_of_birth(minimum_age=18, maximum_age=65)
    return dob.strftime("%Y-%m-%d")


def _pick_gender(cf: ClassifiedField) -> str:
    """Pick a gender value, preferring dropdown options if available."""
    if cf.raw.options:
        return random.choice(cf.raw.options)
    return random.choice(["Male", "Female", "Other"])


def _generic_text(fake: Faker, cf: ClassifiedField) -> str:
    """Fallback: generate sensible text based on the field's input type."""
    if cf.raw.input_type == "textarea":
        return fake.paragraph(nb_sentences=2)
    return fake.word().capitalize()
