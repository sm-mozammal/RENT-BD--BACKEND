import re
from typing import Optional


BD_PHONE_REGEX = re.compile(r'^(?:\+?8801|01)[3-9]\d{8}$')


def normalize_bangladesh_phone(phone: str) -> str:
    """
    Normalizes any valid Bangladesh phone number into international E.164 format:
    e.g. '01712345678' -> '+8801712345678'
    e.g. '8801712345678' -> '+8801712345678'
    e.g. '+8801712345678' -> '+8801712345678'
    """
    clean = re.sub(r'[\s\-()]', '', phone.strip())
    if clean.startswith('+880'):
        return clean
    elif clean.startswith('880'):
        return f'+{clean}'
    elif clean.startswith('01'):
        return f'+88{clean}'
    return clean


def is_valid_bangladesh_phone(phone: str) -> bool:
    """
    Checks if a phone string is a valid Bangladesh mobile operator number (GP, Robi, BL, Teletalk).
    """
    if not phone:
        return False
    clean = re.sub(r'[\s\-()]', '', phone.strip())
    return bool(BD_PHONE_REGEX.match(clean))


def mask_phone_number(phone: str) -> str:
    """
    Masks a phone number for user privacy in public listings:
    e.g. '+8801712345678' -> '+880 17•• ••••78'
    """
    norm = normalize_bangladesh_phone(phone)
    if len(norm) == 14:  # '+8801712345678'
        return f"{norm[:4]} {norm[4:6]}•• ••••{norm[-2:]}"
    return phone
