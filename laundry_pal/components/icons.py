"""Thin line icons drawn with Tkinter canvas primitives (no emoji, no icon files).

Every icon is designed on a 24 x 24 grid and scaled to `size`.
Usage:  icons.draw(surface, "mail", cx, cy, size=20, color=C.MUTED)
"""
import math

from config import C


def _star_points(cx, cy, ro, ri):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        r = ro if i % 2 == 0 else ri
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def draw(s, name, cx, cy, size=20, color=C.NAVY, tags=(), w=1.6, fill=None):
    k = size / 24.0
    lw = w * max(0.85, k)

    def P(x, y):
        return (cx + (x - 12) * k, cy + (y - 12) * k)

    def L(*pts, smooth=False):
        s.line([c for p in pts for c in P(*p)], color, lw, tags, smooth=smooth)

    def R(x1, y1, x2, y2, r=2, f=""):
        a, b = P(x1, y1)
        s.rrect(a, b, (x2 - x1) * k, (y2 - y1) * k, r * k, fill=f, outline=color, width=lw, tags=tags)

    def O(x, y, r, f=""):
        px, py = P(x, y)
        s.oval(px, py, r * k, fill=f, outline=color, width=lw, tags=tags)

    def A(x, y, r, start, extent):
        px, py = P(x, y)
        s.arc(px, py, r * k, start, extent, color, lw, tags)

    def DOT(x, y, r=1.1):
        px, py = P(x, y)
        s.oval(px, py, r * k, fill=color, outline="", tags=tags)

    def POLY(pts, smooth=False, f=""):
        s.poly([c for p in pts for c in P(*p)], fill=f, outline=color, width=lw, smooth=smooth, tags=tags)

    n = name
    if n == "mail":
        R(3, 5.5, 21, 18.5, 2.5); L((3.8, 7), (12, 13), (20.2, 7))
    elif n == "lock":
        R(5, 11, 19, 21, 2.5); A(12, 11, 4, 0, 180); DOT(12, 16)
    elif n == "pin":
        A(12, 10, 6, -25, 230); L((6.7, 12.6), (12, 21), (17.3, 12.6)); O(12, 10, 2.3)
    elif n == "bell":
        POLY([(5, 17), (7, 15), (7, 10.5), (9, 6.5), (12, 5.5), (15, 6.5), (17, 10.5), (17, 15), (19, 17), (5, 17)],
             smooth=True)
        L((12, 3.2), (12, 5.5)); A(12, 19, 2.2, 180, 180)
    elif n == "search":
        O(10.5, 10.5, 6.5); L((15.4, 15.4), (20.5, 20.5))
    elif n == "star":
        POLY(_star_points(12, 12.6, 9.5, 4.2), f=fill or "")
    elif n == "chevron_r":
        L((9.5, 5.5), (16, 12), (9.5, 18.5))
    elif n == "chevron_l":
        L((14.5, 5.5), (8, 12), (14.5, 18.5))
    elif n == "filter":
        L((3.5, 8), (20.5, 8)); L((3.5, 16), (20.5, 16)); O(9, 8, 2.4, f=C.WHITE); O(15, 16, 2.4, f=C.WHITE)
    elif n == "sort":
        L((8, 19), (8, 5)); L((4.5, 8.5), (8, 5), (11.5, 8.5)); L((16, 5), (16, 19)); L((12.5, 15.5), (16, 19), (19.5, 15.5))
    elif n == "home":
        L((3, 11), (12, 3.5), (21, 11)); L((5.5, 9.5), (5.5, 20.5), (18.5, 20.5), (18.5, 9.5)); L((10, 20.5), (10, 14.5), (14, 14.5), (14, 20.5))
    elif n == "orders":
        R(5, 3, 19, 21, 2.5); L((9, 8), (15, 8)); L((9, 12), (15, 12)); L((9, 16), (12.5, 16))
    elif n == "profile":
        O(12, 8, 4); A(12, 21.5, 7.5, 0, 180)
    elif n == "washer":
        R(4.5, 3, 19.5, 21, 2.6); O(12, 13, 4.6); A(12, 13, 2.2, 90, 180); L((8, 6.5), (10.5, 6.5)); DOT(15.5, 6.5, 0.7)
    elif n == "clock":
        O(12, 12, 9); L((12, 7), (12, 12), (15.5, 14))
    elif n == "check_circle":
        O(12, 12, 9); L((8, 12.3), (11, 15.3), (16, 9.5))
    elif n == "cross_circle":
        O(12, 12, 9); L((9, 9), (15, 15)); L((15, 9), (9, 15))
    elif n == "box":
        POLY([(12, 3), (20, 7.5), (20, 16.5), (12, 21), (4, 16.5), (4, 7.5), (12, 3)])
        L((4, 7.5), (12, 12), (20, 7.5)); L((12, 12), (12, 21))
    elif n == "shirt":
        POLY([(8.5, 3.5), (3.5, 7), (5.5, 11), (8, 9.8), (8, 20), (16, 20), (16, 9.8), (18.5, 11), (20.5, 7), (15.5, 3.5)])
        A(12, 3.5, 3.2, 180, 180)
    elif n == "bike":
        O(6, 16, 3.6); O(18, 16, 3.6); L((6, 16), (10, 9), (16.5, 9), (18, 16)); L((10, 9), (12.5, 16), (6, 16)); L((15, 6.5), (17.5, 6.5))
    elif n == "phone":
        POLY([(5.5, 4.5), (9, 4), (10.7, 8.6), (8.6, 10.4), (13.6, 15.4), (15.4, 13.4), (20, 15), (19.5, 18.6), (16.5, 20),
              (9, 17.8), (4.2, 10)], smooth=True)
    elif n == "upi":
        for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            x, y = 12 + sx * 8, 12 + sy * 8
            L((x, y - sy * 4), (x, y), (x - sx * 4, y))
        L((8.5, 12), (15.5, 12))
    elif n == "card":
        R(3, 5.5, 21, 18.5, 2.5); L((3, 10), (21, 10)); L((6.5, 14.5), (10, 14.5))
    elif n == "wallet":
        R(3, 5.5, 21, 19, 2.5); L((3.5, 7.5), (12, 13.5), (20.5, 7.5))
    elif n == "dots":
        DOT(5, 12, 1.9); DOT(12, 12, 1.9); DOT(19, 12, 1.9)
    elif n == "signout":
        L((10, 4), (5, 4), (5, 20), (10, 20)); L((9.5, 12), (20, 12)); L((16, 8), (20, 12), (16, 16))
    elif n == "plus":
        L((12, 5), (12, 19)); L((5, 12), (19, 12))
    elif n == "minus":
        L((5, 12), (19, 12))
    elif n == "close":
        L((6, 6), (18, 18)); L((18, 6), (6, 18))
    elif n == "check":
        L((5, 12.5), (10, 17.5), (19, 7))
    elif n == "trash":
        L((4.5, 7), (19.5, 7)); L((9.5, 7), (9.5, 4.5), (14.5, 4.5), (14.5, 7)); L((6.5, 7), (7.5, 20), (16.5, 20), (17.5, 7))
    else:
        raise KeyError(f"unknown icon {name}")
