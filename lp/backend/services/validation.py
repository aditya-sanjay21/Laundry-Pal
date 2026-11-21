"""Small input validators used by the login / sign-up / address forms."""
import re

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")


def is_email(s):
    return bool(_EMAIL.match(s.strip()))


def phone_digits(s):
    """Returns the last 10 digits if s looks like an Indian mobile number, else ''."""
    d = "".join(ch for ch in s if ch.isdigit())
    if len(d) == 12 and d.startswith("91"):
        d = d[2:]
    return d if len(d) == 10 and d[0] in "6789" else ""


def is_pincode(s):
    return bool(re.fullmatch(r"\d{6}", s.strip()))


def pretty_phone(d):
    return f"+91 {d[:5]} {d[5:]}" if len(d) == 10 else d
