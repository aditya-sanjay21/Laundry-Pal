"""Screen 3 - Laundry Providers (with working Filter and Sort sheets)."""
import database as db
from components import images
from config import C
from screens.base import Screen
from services import booking_service as bs
from services import pricing_service as pr

RATING = [("Any", None), ("4.5+", 4.5), ("4.8+", 4.8)]
PRICE = [("Any", None), ("Up to ₹75", 75), ("Up to ₹85", 85)]
PICKUP = [("Any", None), ("30 min", 30), ("45 min", 45), ("1 hr", 60)]
SORTS = [("Top rated", "rating"), ("Price: low to high", "price"), ("Nearest", "distance"), ("Fastest pickup", "pickup")]


class ProvidersScreen(Screen):
    nav_tab = "home"

    def build(self):
        c, ses = self.c, self.app.session
        service = self.app.service()
        c.header(f"{service['name']} Providers", on_back=self.app.back)
        rows = self.visible(service)
        n = len(rows)
        c.text(20, 145, f"{n} provider{'s' if n != 1 else ''} nearby", 14, fill=C.MUTED)
        active = any(v is not None for v in ses.filters.values())
        for x, w, icon, label, cmd, hot in ((248, 79, "filter", "Filter", self.filter_sheet, active),
                                           (335, 75, "sort", "Sort", self.sort_sheet, False)):
            t = c.new_tag()
            c.rrect(x, 127, w, 36, 11, fill=C.PALE if hot else C.WHITE, outline=C.BLUE if hot else C.BORDER, tags=(t,))
            c.icon(icon, x + 20, 145, 17, C.BLUE if hot else C.NAVY_SOFT, tags=(t,), w=1.4)
            c.text(x + 36, 145, label, 14, fill=C.NAVY, tags=(t,))
            c.on(t, cmd)
        if not rows:
            c.text(215, 330, "No providers match your filters.", 16, fill=C.MUTED, anchor="center")
            c.link(215, 362, "Clear filters", self.clear_filters, 15, anchor="center")
        for i, p in enumerate(rows[:3]):
            y, t = 178 + i * 188, c.new_tag()
            c.rrect(20, y, 390, 176, 14, fill=C.WHITE, outline=C.BORDER, tags=(t,))
            c.photo(33, y + 12, images.load(p["image_list"], 131, 152, 12), tags=(t,))
            c.text(178, y + 23, p["name"], 18, fill=C.NAVY, tags=(t,))
            c.icon("star", 186, y + 47, 17, C.STAR, tags=(t,), w=1.3)
            c.text(199, y + 47, f"{p['rating']}", 14, fill=C.NAVY, tags=(t,))
            c.text(178, y + 70, bs.fmt_pickup_wait(p["pickup_min"]), 13, fill=C.GREEN_TEXT, tags=(t,))
            c.text(178, y + 146, f"{pr.money(pr.unit_price(p, service))} / kg", 16, fill=C.NAVY, tags=(t,))
            c.rrect(364, y + 130, 34, 34, 9, fill=C.BLUE, tags=(t,))
            c.icon("chevron_r", 381, y + 147, 16, C.WHITE, tags=(t,), w=1.8)
            c.on(t, lambda pid=p["id"]: self.open_provider(pid))
        if n > 3:
            c.text(215, 760, f"+ {n - 3} more — use Filter to narrow the list", 13, fill=C.MUTED, anchor="center")

    # ------------------------------------------------------------ data
    def visible(self, service):
        ses, f = self.app.session, self.app.session.filters
        rows = db.providers()
        if ses.query:
            rows = [p for p in rows if ses.query in p["name"].lower()]
        if f["rating"]:
            rows = [p for p in rows if p["rating"] >= f["rating"]]
        if f["price"]:
            rows = [p for p in rows if p["price_per_kg"] <= f["price"]]
        if f["pickup"]:
            rows = [p for p in rows if p["pickup_min"] <= f["pickup"]]
        key = {"rating": lambda p: -p["rating"], "price": lambda p: p["price_per_kg"],
               "distance": lambda p: p["distance_km"], "pickup": lambda p: p["pickup_min"]}[ses.sort]
        return sorted(rows, key=key)

    def open_provider(self, pid):
        self.app.session.provider_id = pid
        self.app.go("details")

    def clear_filters(self):
        self.app.session.filters = {"rating": None, "price": None, "pickup": None}
        self.app.session.query = ""
        self.redraw()

    # ------------------------------------------------------------ sheets
    def filter_sheet(self, tmp=None):
        c = self.c
        tmp = tmp if tmp is not None else dict(self.app.session.filters)
        top = c.open_sheet("Filter providers", 470)
        y = top + 78
        for title, key, options in (("Minimum rating", "rating", RATING), ("Price per kg", "price", PRICE),
                                    ("Pickup time", "pickup", PICKUP)):
            c.text(24, y, title, 14, "bold", C.MUTED, tags=("ov",))
            x = 24
            for label, value in options:
                x += c.chip(x, y + 18, label, tmp[key] == value,
                            lambda k=key, v=value: (tmp.__setitem__(k, v), self.filter_sheet(tmp))) + 8
            y += 86
        c.button(24, 852 - 20, 130, 50, "Reset", lambda: self.filter_sheet({"rating": None, "price": None, "pickup": None}),
                 kind="soft", size=15, tags=("ov",))
        c.button(166, 852 - 20, 240, 50, "Apply filters", lambda: self.apply_filters(tmp), size=15, tags=("ov",))

    def apply_filters(self, tmp):
        self.app.session.filters = dict(tmp)
        self.c.close_sheet()
        self.redraw()

    def sort_sheet(self):
        c = self.c
        top = c.open_sheet("Sort by", 380)
        y = top + 70
        for label, key in SORTS:
            t, sel = c.new_tag(), self.app.session.sort == key
            c.rrect(24, y, 382, 52, 14, fill=C.PALE if sel else C.WHITE, outline=C.BLUE if sel else C.BORDER, tags=("ov", t))
            c.text(44, y + 26, label, 15, "bold" if sel else "normal", C.NAVY, tags=("ov", t))
            if sel:
                c.icon("check", 380, y + 26, 18, C.BLUE, tags=("ov", t), w=2)
            c.on(t, lambda k=key: self.set_sort(k))
            y += 62

    def set_sort(self, key):
        self.app.session.sort = key
        self.c.close_sheet()
        self.redraw()
