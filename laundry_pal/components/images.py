"""Pillow helpers: load a photo, crop it to a box ("cover"), round the corners."""
import os

from PIL import Image, ImageDraw, ImageTk

import config
from config import C, sc

_cache = {}


def load(name, w, h, radius=0, corners=(True, True, True, True), circle=False):
    """Returns a Tk PhotoImage of logical size w x h.  Missing files give a pale placeholder."""
    key = (name, w, h, radius, corners, circle, config.SCALE)
    if key in _cache:
        return _cache[key]
    W, H = sc(w), sc(h)
    path = os.path.join(config.IMG_DIR, name) if name else ""
    try:
        im = Image.open(path).convert("RGB")
    except (OSError, ValueError):
        im = Image.new("RGB", (W, H), C.PALE)
    k = max(W / im.width, H / im.height)                      # scale to cover the box
    im = im.resize((max(W, round(im.width * k)), max(H, round(im.height * k))), Image.LANCZOS)
    left, top = (im.width - W) // 2, (im.height - H) // 2
    im = im.crop((left, top, left + W, top + H)).convert("RGBA")

    ss = 4                                                    # super-sampled mask = smooth edges
    mask = Image.new("L", (W * ss, H * ss), 0)
    d = ImageDraw.Draw(mask)
    if circle:
        d.ellipse((0, 0, W * ss - 1, H * ss - 1), fill=255)
    elif radius:
        d.rounded_rectangle((0, 0, W * ss - 1, H * ss - 1), radius=sc(radius) * ss, fill=255, corners=corners)
    else:
        d.rectangle((0, 0, W * ss, H * ss), fill=255)
    im.putalpha(mask.resize((W, H), Image.LANCZOS))
    _cache[key] = ImageTk.PhotoImage(im)
    return _cache[key]


def dim_layer(alpha=110):
    """Semi-transparent dark layer used behind bottom sheets."""
    key = ("dim", alpha, config.SCALE)
    if key not in _cache:
        _cache[key] = ImageTk.PhotoImage(Image.new("RGBA", (sc(config.W), sc(config.H)), (12, 30, 48, alpha)))
    return _cache[key]
