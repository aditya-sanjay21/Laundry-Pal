"""Screen 2 - Home."""
import database as db
from components import images
from config import C
from screens.base import Screen
from services import booking_service as bs


class HomeScreen(Screen):
    nav_tab = "home"

    def build(self):
        c, app = self.c, self.app
        user = app.session.user
        addr = db.default_address(user["id"])
        # location row
        c.rrect(20, 58, 42, 42, 13, fill=C.PALE)
        c.icon("pin", 41, 79, 22, C.BLUE, w=1.5)
        c.text(72, 70, "Your location", 11, fill=C.MUTED)
        c.text(72, 87, f"{addr['area']}, {addr['city']}" if addr else "Add an address", 15, "bold", C.NAVY)
        bell = c.new_tag()
        c.rect(372, 62, 54, 36, fill=C.BG, tags=(bell,))
        c.icon("bell", 399, 80, 23, C.NAVY, tags=(bell,), w=1.5)
        c.on(bell, lambda: c.toast("You have no new notifications."))
        # search
        self.search = c.field(20, 113, 390, 50, "Search services or providers", "search", size=15, r=14)
        self.search.bind("<Return>", lambda _e: self.do_search())
        # services
        c.text(20, 187, "What do you need?", 20, fill=C.NAVY)
        for i, s in enumerate(db.services()):
            y, t = 212 + i * 106, c.new_tag()
            c.rrect(20, y, 390, 94, 14, fill=C.WHITE, outline=C.BORDER, tags=(t,))
            c.photo(21, y + 1, images.load(s["image"], 111, 92, 13, (True, False, False, True)), tags=(t,))
            c.text(146, y + 37, s["name"], 18, fill=C.NAVY, tags=(t,))
            c.text(146, y + 60, s["subtitle"], 13, fill=C.MUTED, tags=(t,))
            c.rrect(355, y + 28, 38, 38, 11, fill=C.PALE_BTN, tags=(t,))
            c.icon("chevron_r", 374, y + 47, 18, C.BLUE, tags=(t,), w=1.6)
            c.on(t, lambda k=s["key"]: self.pick_service(k))
        # nearby providers
        c.text(20, 544, "Nearby Providers", 20, fill=C.NAVY)
        c.link(410, 544, "View all", lambda: self.pick_service(app.session.service_key), 14)
        near = sorted(db.providers(), key=lambda p: p["distance_km"])[:2]
        for i, p in enumerate(near):
            x, t = 20 + i * 200, c.new_tag()
            c.rrect(x, 567, 190, 63, 14, fill=C.PALE if i == 0 else C.GREEN_PALE, tags=(t,))
            c.text(x + 12, 588, p["name"], 15, "bold", C.NAVY, tags=(t,))
            c.icon("star", x + 20, 610, 16, C.STAR, tags=(t,), w=1.3)
            c.text(x + 32, 610, f"{p['rating']}", 14, fill=C.NAVY, tags=(t,))
            c.text(x + 178, 610, f"{p['distance_km']} km", 12, fill=C.MUTED, anchor="e", tags=(t,))
            c.on(t, lambda pid=p["id"]: self.open_provider(pid))

    def pick_service(self, key):
        self.app.session.service_key = key
        self.app.session.query = ""
        self.app.go("providers")

    def open_provider(self, pid):
        self.app.session.provider_id = pid
        self.app.go("details")

    def do_search(self):
        q = self.search.value().lower()
        if not q:
            return self.c.toast("Type a service or provider name to search.")
        for s in db.services():                       # "iron" -> Ironing, "dry" -> Dry Clean ...
            if q in s["name"].lower() or s["name"].lower().startswith(q[:4]):
                self.app.session.service_key = s["key"]
                self.app.session.query = ""
                return self.app.go("providers")
        if not any(q in p["name"].lower() for p in db.providers()):
            return self.c.toast(f"No service or provider matches “{q}”.", error=True)
        self.app.session.query = q
        self.app.go("providers")
