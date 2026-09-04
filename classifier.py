"""Classify raw form fields into semantic types via keyword matching."""

from models import ClassifiedField, FieldType, FormField


# ---------------------------------------------------------------------------
# Keyword → FieldType mapping
# ---------------------------------------------------------------------------
# Order matters: more specific patterns are checked first.

_KEYWORD_MAP: list[tuple[list[str], FieldType]] = [
    # Email
    (["email", "e-mail", "e_mail", "emailaddress"], FieldType.EMAIL),
    # Phone
    (["phone", "tel", "mobile", "cell", "fax", "phonenumber"], FieldType.PHONE),
    # Password (confirm before regular – more specific first)
    (["confirm_password", "confirmpassword", "confirm-password", "password_confirm",
     "password_confirmation", "passwordconfirmation", "repassword", "re_password",
     "re-password", "pass_confirm", "pass2", "password2", "pwd_confirm", "repeat_password",
     "repeatpassword", "verify_password", "verifypassword"], FieldType.CONFIRM_PASSWORD),
    (["password", "passwd", "pass", "pwd", "secret"], FieldType.PASSWORD),
    # Username
    (["username", "user_name", "userid", "login", "screenname", "handle"], FieldType.USERNAME),
    # Name (check multi-word patterns before single-word)
    (["fullname", "full_name", "full-name", "your_name", "your-name"], FieldType.FULL_NAME),
    (["firstname", "first_name", "first-name", "fname", "given_name", "givenname"], FieldType.FIRST_NAME),
    (["lastname", "last_name", "last-name", "lname", "surname", "family_name", "familyname"], FieldType.LAST_NAME),
    (["middlename", "middle_name", "middle-name", "mname"], FieldType.FIRST_NAME),
    # Age / DOB
    (["dob", "date_of_birth", "dateofbirth", "birthdate", "birth_date", "birthday"], FieldType.DATE_OF_BIRTH),
    (["age"], FieldType.AGE),
    # Gender
    (["gender", "sex"], FieldType.GENDER),
    # Address parts (specific before generic)
    (["zipcode", "zip_code", "zip", "postalcode", "postal_code", "postal", "pincode", "pin_code"], FieldType.ZIP_CODE),
    (["city", "town", "locality"], FieldType.CITY),
    (["state", "province", "region"], FieldType.STATE),
    (["street", "street_address", "streetaddress", "address_line", "addressline", "addr1", "addr2"], FieldType.STREET),
    (["country", "nation"], FieldType.COUNTRY),
    (["address", "addr", "location"], FieldType.ADDRESS),
    # Professional
    (["company", "org", "organization", "organisation", "employer"], FieldType.COMPANY),
    (["job", "jobtitle", "job_title", "occupation", "position", "role"], FieldType.JOB_TITLE),
    # Web
    (["website", "url", "homepage", "webpage", "site", "blog"], FieldType.WEBSITE),
    # Financial
    (["ssn", "social_security", "socialsecurity", "sin"], FieldType.SSN),
    (["cvv", "cvc", "securitycode", "security_code"], FieldType.CVV),
    (["expiry", "expiration", "exp_date", "expdate", "exp_month", "exp_year"], FieldType.EXPIRY_DATE),
    (["creditcard", "credit_card", "cardnumber", "card_number", "ccnumber", "cc_number"], FieldType.CREDIT_CARD),
]

# HTML autocomplete → FieldType
_AUTOCOMPLETE_MAP: dict[str, FieldType] = {
    "email": FieldType.EMAIL,
    "tel": FieldType.PHONE,
    "tel-national": FieldType.PHONE,
    "given-name": FieldType.FIRST_NAME,
    "family-name": FieldType.LAST_NAME,
    "name": FieldType.FULL_NAME,
    "username": FieldType.USERNAME,
    "new-password": FieldType.PASSWORD,
    "current-password": FieldType.PASSWORD,
    "bday": FieldType.DATE_OF_BIRTH,
    "sex": FieldType.GENDER,
    "street-address": FieldType.STREET,
    "address-line1": FieldType.STREET,
    "address-line2": FieldType.STREET,
    "address-level2": FieldType.CITY,
    "address-level1": FieldType.STATE,
    "postal-code": FieldType.ZIP_CODE,
    "country-name": FieldType.COUNTRY,
    "organization": FieldType.COMPANY,
    "url": FieldType.WEBSITE,
    "cc-number": FieldType.CREDIT_CARD,
    "cc-csc": FieldType.CVV,
    "cc-exp": FieldType.EXPIRY_DATE,
}

# HTML input type → FieldType (lowest priority fallback)
_INPUT_TYPE_MAP: dict[str, FieldType] = {
    "email": FieldType.EMAIL,
    "tel": FieldType.PHONE,
    "password": FieldType.PASSWORD,
    "url": FieldType.WEBSITE,
    "number": FieldType.NUMBER,
    "date": FieldType.DATE_OF_BIRTH,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def classify_fields(fields: list[FormField]) -> list[ClassifiedField]:
    """Classify a list of raw form fields into semantic types."""
    return [_classify_single(f) for f in fields]


def _classify_single(field: FormField) -> ClassifiedField:
    """Classify a single ``FormField`` using layered heuristics.

    Priority order:
    1. autocomplete attribute
    2. Keyword matching on name / id / placeholder / label
    3. HTML input type fallback
    4. Generic TEXT fallback
    """
    # 1. autocomplete attribute
    if field.autocomplete:
        ac = field.autocomplete.lower().strip()
        if ac in _AUTOCOMPLETE_MAP:
            return ClassifiedField(raw=field, semantic_type=_AUTOCOMPLETE_MAP[ac])

    # 2. Keyword matching across all text hints
    haystack = " ".join([
        field.name.lower(),
        field.field_id.lower(),
        field.placeholder.lower(),
        field.label.lower(),
    ])
    # Remove common separators so "first-name" matches "firstname"
    haystack_flat = haystack.replace("-", "").replace("_", "").replace(" ", "")

    for keywords, field_type in _KEYWORD_MAP:
        for kw in keywords:
            kw_flat = kw.replace("-", "").replace("_", "").replace(" ", "")
            if kw_flat in haystack_flat:
                return ClassifiedField(raw=field, semantic_type=field_type)

    # 3. HTML input type
    if field.input_type in _INPUT_TYPE_MAP:
        return ClassifiedField(
            raw=field, semantic_type=_INPUT_TYPE_MAP[field.input_type]
        )

    # 4. Check if it's a name-only field with just "name" in hints
    if "name" in haystack:
        return ClassifiedField(raw=field, semantic_type=FieldType.FULL_NAME)

    # 5. Fallback
    return ClassifiedField(raw=field, semantic_type=FieldType.TEXT)
