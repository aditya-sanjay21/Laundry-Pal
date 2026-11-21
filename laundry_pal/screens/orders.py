"""Orders tab (bottom navigation) - order history; tap an order to track it."""
import database as db
from config import C
from screens.base import Screen
from services import booking_service as bs
from services import pricing_service as pr

MAX_ROWS = 7


class OrdersScreen(Screen):
    nav_tab = "orders"

    def build(self):
        c, app = self.c, self.app
        c.header("My Orders")
        rows = db.orders(app.session.user["id"])
        if not rows:
            c.text(215, 400, "No orders yet", 18, "bold", C.NAVY, "center")
            c.text(215, 430, "Your bookings will appear here.", 14, fill=C.MUTED, anchor="center")
            return
        for i, o in enumerate(rows[:MAX_ROWS]):
            y, t = 128 + i * 98, c.new_tag()
            service = db.service(o["service_key"])
            c.rrect(20, y, 390, 86, 16, fill=C.WHITE, outline=C.BORDER, tags=(t,))
            c.rrect(34, y + 20, 46, 46, 13, fill=C.PALE, tags=(t,))
            c.icon("washer", 57, y + 43, 24, C.BLUE, tags=(t,), w=1.4)
            c.text(94, y + 25, o["code"], 16, "bold", C.NAVY, tags=(t,))
            c.text(94, y + 48, f"{service['name']} · {o['weight']} kg", 13, fill=C.MUTED, tags=(t,))
            c.text(94, y + 68, bs.fmt_dt(o["created_at"]), 11, fill=C.FAINT, tags=(t,))
            c.text(394, y + 25, pr.money(o["total"]), 16, "bold", C.NAVY, "e", tags=(t,))
            label = bs.status_label(o)
            color = C.DANGER if o["cancelled"] else (C.GREEN_TEXT if o["stage"] == 4 else C.BLUE)
            w = c.text_w(label, 12, "bold") + 20
            c.rrect(394 - w, y + 44, w, 26, 13, fill=C.DANGER_BG if o["cancelled"] else (
                C.GREEN_PALE if o["stage"] == 4 else C.PALE), tags=(t,))
            c.text(394 - w / 2, y + 57, label, 12, "bold", color, "center", tags=(t,))
            c.on(t, lambda oid=o["id"]: app.go("tracking", order_id=oid))
        if len(rows) > MAX_ROWS:
            c.text(215, 128 + MAX_ROWS * 98 + 6, f"Showing latest {MAX_ROWS} of {len(rows)} orders", 12, fill=C.MUTED, anchor="center")
