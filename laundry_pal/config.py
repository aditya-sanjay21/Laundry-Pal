"""Central design system: window size, colours, fonts and the scale helper.

All screens are designed on a 430 x 932 "logical" canvas (the size of the Figma
frames).  Every coordinate in the code is a logical coordinate; `sc()` converts
it to real pixels so the whole UI shrinks on small laptop screens.
"""
import os
import tkinter.font as tkfont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "assets", "images")
ICON_DIR = os.path.join(BASE_DIR, "assets", "icons")
DB_PATH = os.path.join(BASE_DIR, "laundry_pal.db")

W, H = 430, 932          # logical phone size
SCALE = 1.0              # set at start-up by app.py


def set_scale(value):
    global SCALE
    SCALE = value


def sc(v):
    """logical units -> real pixels"""
    return int(round(v * SCALE))


class C:
    """Colour palette (sampled from the reference screenshots)."""
    BG = "#F7FAFC"
    WHITE = "#FFFFFF"
    NAVY = "#16324A"
    NAVY_SOFT = "#324B60"
    BLUE = "#1976D2"
    BLUE_DARK = "#1565B8"
    PALE = "#EDF6FE"
    PALE_BTN = "#E3F0FC"
    BORDER = "#DCE6EE"
    HEADER_LINE = "#E6EBF0"
    MUTED = "#6B7F93"
    FAINT = "#9FB3C8"
    GREEN = "#28A680"
    GREEN_DOT = "#4FB699"
    GREEN_TEXT = "#22A06B"
    GREEN_PALE = "#EAF8F3"
    STAR = "#F2A93B"
    DANGER = "#D14343"
    DANGER_BG = "#FFF3F3"
    DANGER_BORDER = "#F3C7C7"
    RADIO = "#C9D7E4"
    STATUS = "#16324A"
    INDICATOR = "#455B6E"


FONT_CANDIDATES = ("Inter", "Segoe UI", "SF Pro Text", "Helvetica Neue",
                   "Helvetica", "Arial", "DejaVu Sans")
_family = None
_fonts = {}


def resolve_font_family(root):
    global _family
    available = set(tkfont.families(root))
    _family = next((f for f in FONT_CANDIDATES if f in available), "TkDefaultFont")
    return _family


def get_font(size, weight="normal"):
    """size is in logical pixels; weight is 'normal' or 'bold'."""
    key = (size, weight, SCALE)
    if key not in _fonts:
        _fonts[key] = tkfont.Font(family=_family, size=-max(8, sc(size)), weight=weight)
    return _fonts[key]
