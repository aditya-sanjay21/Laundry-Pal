"""Surface = a tk.Canvas with drawing helpers that use *logical* coordinates.

Everything on screen is drawn here: rounded cards, text, icons, buttons, the
status bar, bottom sheets and toast messages.  Real Tkinter `Entry` widgets are
embedded for text input.
"""
import datetime as dt
import tkinter as tk

import config
from config import C, sc
from components import icons, images


def _round_points(x1, y1, x2, y2, r):
    r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    return [x1 + r, y1, x1 + r, y1, x2 - r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y1 + r, x2, y2 - r, x2, y2 - r,
            x2, y2, x2 - r, y2, x2 - r, y2, x1 + r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y2 - r, x1, y1 + r,
            x1, y1 + r, x1, y1]


class PlaceholderEntry(tk.Entry):
    """tk.Entry with grey placeholder text (Tkinter has none built in)."""

    def __init__(self, master, placeholder="", secret=False, **kw):
        super().__init__(master, **kw)
        self.placeholder, self.secret, self._ph = placeholder, secret, False
        self.bind("<FocusIn>", self._focus_in, add="+")
        self.bind("<FocusOut>", self._focus_out, add="+")
        self._focus_out()

    def _focus_in(self, _e=None):
        if self._ph:
            self.delete(0, "end")
            self._ph = False
            self.config(fg=C.NAVY, show="•" if self.secret else "")

    def _focus_out(self, _e=None):
        if not tk.Entry.get(self):
            self._ph = True
            self.config(fg=C.MUTED, show="")
            self.insert(0, self.placeholder)

    def value(self):
        return "" if self._ph else tk.Entry.get(self).strip()

    def set(self, text):
        self.delete(0, "end")
        self._ph = False
        self.config(fg=C.NAVY, show="•" if self.secret else "")
        self.insert(0, text)
        if not text:
            self._focus_out()


class Surface(tk.Canvas):
    def __init__(self, master, bg=C.BG):
        super().__init__(master, width=sc(config.W), height=sc(config.H), bg=bg, highlightthickness=0, bd=0)
        self._imgs, self._widgets, self._n = [], [], 0
        self._toast_job = None

    # ------------------------------------------------------------ primitives
    def font(self, size, weight="normal"):
        return config.get_font(size, weight)

    def text_w(self, s, size=14, weight="normal"):
        """Width of text in logical units."""
        return self.font(size, weight).measure(s) / config.SCALE

    def new_tag(self):
        self._n += 1
        return f"t{self._n}"

    @staticmethod
    def _px(pts):
        return [sc(v) for v in pts]

    def rect(self, x, y, w, h, fill="", outline="", tags=()):
        return self.create_rectangle(sc(x), sc(y), sc(x + w), sc(y + h), fill=fill, outline=outline, width=1, tags=tags)

    def rrect(self, x, y, w, h, r=12, fill="", outline="", width=1, tags=()):
        pts = _round_points(sc(x), sc(y), sc(x + w), sc(y + h), sc(r))
        return self.create_polygon(pts, smooth=True, splinesteps=14, fill=fill, outline=outline,
                                   width=max(1.0, width * config.SCALE) if outline else 0, tags=tags)

    def poly(self, pts, fill="", outline="", width=1, smooth=False, tags=()):
        return self.create_polygon(self._px(pts), smooth=smooth, fill=fill, outline=outline or "",
                                   width=max(1.0, width * config.SCALE) if outline else 0, joinstyle="round", tags=tags)

    def oval(self, cx, cy, r, fill="", outline="", width=1, tags=()):
        return self.create_oval(sc(cx - r), sc(cy - r), sc(cx + r), sc(cy + r), fill=fill, outline=outline,
                                width=max(1.0, width * config.SCALE) if outline else 0, tags=tags)

    def arc(self, cx, cy, r, start, extent, color, width=1.6, tags=()):
        return self.create_arc(sc(cx - r), sc(cy - r), sc(cx + r), sc(cy + r), start=start, extent=extent,
                               style="arc", outline=color, width=max(1.0, width * config.SCALE), tags=tags)

    def line(self, pts, fill, width=1.6, tags=(), smooth=False):
        return self.create_line(*self._px(pts), fill=fill, width=max(1.0, width * config.SCALE), capstyle="round",
                                joinstyle="round", smooth=smooth, tags=tags)

    def text(self, x, y, s, size=14, weight="normal", fill=C.NAVY, anchor="w", tags=(), width=0, justify="left"):
        return self.create_text(sc(x), sc(y), text=s, font=self.font(size, weight), fill=fill, anchor=anchor,
                                tags=tags, width=sc(width) if width else 0, justify=justify)

    def photo(self, x, y, img, anchor="nw", tags=()):
        self._imgs.append(img)
        return self.create_image(sc(x), sc(y), image=img, anchor=anchor, tags=tags)

    def icon(self, name, cx, cy, size=20, color=C.NAVY, tags=(), **kw):
        icons.draw(self, name, cx, cy, size, color, tags, **kw)

    def on(self, tag, callback):
        """Make every canvas item with this tag clickable."""
        self.tag_bind(tag, "<Button-1>", lambda e: callback())
        self.tag_bind(tag, "<Enter>", lambda e: self.config(cursor="hand2"), add="+")
        self.tag_bind(tag, "<Leave>", lambda e: self.config(cursor=""), add="+")

    # ------------------------------------------------------------ components
    def button(self, x, y, w, h, label, command, kind="primary", size=16, r=14, tags=()):
        styles = {"primary": (C.BLUE, C.BLUE_DARK, "", C.WHITE),
                  "danger": (C.DANGER_BG, "#FFE8E8", C.DANGER_BORDER, C.DANGER),
                  "outline": (C.WHITE, C.PALE, C.BLUE, C.BLUE),
                  "soft": (C.PALE, C.PALE_BTN, "", C.BLUE),
                  "success": (C.GREEN, "#1F8F6D", "", C.WHITE)}
        fill, hover, outline, fg = styles[kind]
        t = self.new_tag()
        shape = self.rrect(x, y, w, h, r, fill=fill, outline=outline, tags=(t,) + tuple(tags))
        self.text(x + w / 2, y + h / 2, label, size, "bold", fg, "center", tags=(t,) + tuple(tags))
        self.on(t, command)
        self.tag_bind(t, "<Enter>", lambda e: self.itemconfig(shape, fill=hover), add="+")
        self.tag_bind(t, "<Leave>", lambda e: self.itemconfig(shape, fill=fill), add="+")
        return t

    def link(self, x, y, label, command, size=14, anchor="e", color=C.BLUE, weight="normal"):
        t = self.new_tag()
        self.text(x, y, label, size, weight, color, anchor, tags=(t,))
        self.on(t, command)
        return t

    def field(self, x, y, w, h, placeholder, icon=None, secret=False, group="main", text="", size=16, r=16):
        """Rounded white input with a real tk.Entry inside."""
        ring = self.rrect(x, y, w, h, r, fill=C.WHITE, outline=C.BORDER, tags=(group,))
        ex = x + 48 if icon else x + 18
        if icon:
            self.icon(icon, x + 26, y + h / 2, 20, C.MUTED, tags=(group,))
        e = PlaceholderEntry(self, placeholder=placeholder, secret=secret, bd=0, highlightthickness=0, relief="flat",
                             bg=C.WHITE, fg=C.NAVY, font=self.font(size), insertbackground=C.NAVY,
                             disabledbackground=C.WHITE)
        self.create_window(sc(ex), sc(y + h / 2), window=e, anchor="w", width=sc(w - (ex - x) - 14),
                           height=sc(min(h - 16, 34)), tags=(group,))
        e.bind("<FocusIn>", lambda _e: self.itemconfig(ring, outline=C.BLUE), add="+")
        e.bind("<FocusOut>", lambda _e: self.itemconfig(ring, outline=C.BORDER), add="+")
        if text:
            e.set(text)
        e.ring = ring
        self._widgets.append((group, e))
        return e

    def mark_error(self, entry, on=True):
        self.itemconfig(entry.ring, outline=C.DANGER if on else C.BORDER)

    def text_width_center(self, parts, cy, size=14):
        """Draw several (text, weight, colour) parts centred as one line."""
        total = sum(self.text_w(t, size, w) for t, w, _ in parts)
        x = config.W / 2 - total / 2
        out = []
        for t, w, col in parts:
            out.append(self.text(x, cy, t, size, w, col, "w"))
            x += self.text_w(t, size, w)
        return out

    # ------------------------------------------------------------ phone chrome
    def status_bar(self):
        self.text(24, 29, dt.datetime.now().strftime("%I:%M").lstrip("0"), 15, "bold", C.STATUS)
        for i, hgt in enumerate((4, 6.5, 9, 11.5)):                       # signal bars
            x = 335 + i * 5
            self.rrect(x, 34 - hgt, 3, hgt, 1, fill=C.STATUS)
        for r in (3.5, 7, 10.5):                                          # wifi
            self.arc(367, 36, r, 45, 90, C.STATUS, 2)
        self.oval(367, 35, 1.4, fill=C.STATUS)
        self.rrect(382, 23, 23, 12, 3.5, fill="", outline=C.STATUS, width=1.2)   # battery
        self.rrect(384, 25, 19, 8, 2, fill=C.STATUS)
        self.rrect(406, 27, 2, 4, 1, fill=C.STATUS)

    def home_indicator(self):
        self.rrect(143, 917, 144, 5, 2.5, fill=C.INDICATOR)

    def frame_border(self):
        self.rrect(0.5, 0.5, config.W - 1, config.H - 1, 30, fill="", outline=C.BORDER)

    def header(self, title, on_back=None, right=None):
        """White app bar (y 50-111) with centred title, optional back arrow and right link."""
        self.rect(0, 50, config.W, 61, fill=C.WHITE)
        self.line([0, 111, config.W, 111], C.HEADER_LINE, 1)
        self.text(config.W / 2, 81, title, 20, "bold", C.NAVY, "center")
        if on_back:
            t = self.new_tag()
            self.rect(8, 56, 52, 50, fill=C.WHITE, outline="", tags=(t,))
            self.icon("chevron_l", 32, 81, 22, C.NAVY_SOFT, tags=(t,), w=1.5)
            self.on(t, on_back)
        if right:
            self.link(410, 81, right[0], right[1], 15)

    # ------------------------------------------------------------ bottom sheet / toast
    def open_sheet(self, title, height):
        """Dim the screen and draw a white bottom sheet.  Returns the y of its top edge."""
        self.close_sheet()
        dim = self.photo(0, 0, images.dim_layer(), tags=("ov",))
        self.tag_bind(dim, "<Button-1>", lambda e: self.close_sheet())
        top = config.H - height
        self.rrect(0, top, config.W, height + 40, 26, fill=C.WHITE, tags=("ov",))
        self.rrect(config.W / 2 - 20, top + 9, 40, 4, 2, fill=C.BORDER, tags=("ov",))
        self.text(24, top + 40, title, 19, "bold", C.NAVY, "w", tags=("ov",))
        x = self.new_tag()
        self.oval(config.W - 36, top + 40, 15, fill=C.PALE, tags=("ov", x))
        self.icon("close", config.W - 36, top + 40, 14, C.MUTED, tags=("ov", x))
        self.on(x, self.close_sheet)
        return top

    def close_sheet(self):
        for group, widget in list(self._widgets):
            if group == "ov":
                widget.destroy()
        self._widgets = [(g, w) for g, w in self._widgets if g != "ov"]
        self.delete("ov")
        self.focus_set()

    def chip(self, x, y, label, selected, command, size=14, h=38, pad=18):
        """Selectable pill. Returns its width so callers can lay chips out in a row."""
        w = self.text_w(label, size, "bold" if selected else "normal") + pad * 2
        t = self.new_tag()
        self.rrect(x, y, w, h, h / 2, fill=C.BLUE if selected else C.PALE, tags=("ov", t))
        self.text(x + w / 2, y + h / 2, label, size, "bold" if selected else "normal",
                  C.WHITE if selected else C.NAVY, "center", tags=("ov", t))
        self.on(t, command)
        return w

    def toast(self, message, error=False):
        self.delete("toast")
        if self._toast_job:
            self.after_cancel(self._toast_job)
        w = min(config.W - 40, self.text_w(message, 14) + 44)
        x, y = (config.W - w) / 2, config.H - 118
        self.rrect(x, y, w, 44, 14, fill=C.DANGER if error else C.NAVY, tags=("toast",))
        self.text(config.W / 2, y + 22, message, 14, "normal", C.WHITE, "center", tags=("toast",))
        self.tag_raise("toast")
        self._toast_job = self.after(2400, lambda: self.delete("toast"))

    def destroy_widgets(self):
        for _g, w in self._widgets:
            w.destroy()
        self._widgets.clear()
