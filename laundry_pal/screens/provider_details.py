"""Screen 4 - Provider Details."""
from components import images
from config import C
from screens.base import Screen
from services import pricing_service as pr


class ProviderDetailsScreen(Screen):
    def build(self):
        c, app = self.c, self.app
        p, service = app.provider(), app.service()
        c.header(p["name"], on_back=app.back)
        c.photo(20, 128, images.load(p["image_hero"] or p["image_list"], 390, 252, 20))
        c.text(20, 411, p["name"], 24, "bold", C.NAVY)
        c.icon("star", 378, 421, 17, C.STAR, w=1.3)
        c.text(410, 421, f"{p['rating']}", 14, fill=C.NAVY, anchor="e")
        c.text(20, 439, f"{p['address']} · {p['distance_km']} km away", 14, fill=C.MUTED)
        # info card
        c.rrect(20, 462, 390, 198, 16, fill=C.WHITE, outline=C.BORDER)
        rows = [("Service", service["label"], "washer", C.PALE, C.BLUE),
                ("Details", p["details_text"], "clock", C.GREEN_PALE, C.GREEN),
                ("Quality", p["quality_text"], "check_circle", C.PALE, C.BLUE)]
        for i, (label, value, icon, bg, fg) in enumerate(rows):
            cy = 497 + i * 64.5
            c.rrect(36, cy - 19, 38, 38, 10, fill=bg)
            c.icon(icon, 55, cy, 20, fg, w=1.4)
            c.text(86, cy - 11, label, 12, fill=C.MUTED)
            c.text(86, cy + 8, value, 15, fill=C.NAVY)
            if i < 2:
                c.line([36, cy + 32, 394, cy + 32], C.BORDER, 1)
        # price panel
        c.rrect(20, 677, 390, 72, 14, fill=C.PALE)
        c.text(36, 699, "Starting from", 13, fill=C.MUTED)
        c.text(36, 724, f"{pr.money(pr.unit_price(p, service))} / kg", 24, "bold", C.NAVY)
        c.text(394, 711, f"Min. order {pr.money(p['min_order'])}", 13, fill=C.MUTED, anchor="e")
        c.button(20, 836, 390, 56, "Book Now", self.book)

    def book(self):
        app = self.app
        p, service, user = app.provider(), app.service(), app.session.user
        import database as db
        addr = db.default_address(user["id"])
        app.session.booking = {"weight": pr.default_weight(p, service), "day": "Today", "slot": pr.SLOTS[0],
                               "address_id": addr["id"] if addr else None, "payment": "upi"}
        app.go("checkout")
