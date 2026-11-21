"""Screen 6 - Order Tracking (persistent status + simulate-progress button)."""
import database as db
from config import C
from screens.base import Screen
from services import booking_service as bs

DOT_Y = [272, 353, 436, 548]       # y of the four timeline dots (taken from the design)
CARD_Y = [261, 343, 425, 507]


class TrackingScreen(Screen):
    def build(self):
        c, app = self.c, self.app
        oid = self.params.get("order_id") or app.session.order_id
        self.order = db.order(oid) if oid else db.latest_order(app.session.user["id"])
        o = self.order
        c.header("Order Tracking", on_back=app.back)
        if not o:
            c.text(215, 400, "You have no orders yet.", 16, fill=C.MUTED, anchor="center")
            return c.button(115, 430, 200, 50, "Book a wash", lambda: app.tab("home"), size=15)
        app.session.order_id = o["id"]
        # navy summary card
        c.rrect(20, 130, 390, 74, 14, fill=C.NAVY)
        c.text(36, 154, "Order ID", 12, fill=C.FAINT)
        c.text(36, 178, o["code"], 19, fill=C.WHITE)
        c.text(394, 157, "Estimated delivery", 12, fill=C.FAINT, anchor="e")
        eta = "Cancelled" if o["cancelled"] else ("Delivered" if o["stage"] == 4 else bs.fmt_dt(o["eta"]))
        c.text(394, 178, eta, 14, "bold", C.WHITE, "e")
        c.text(20, 233, "Your laundry's journey", 20, fill=C.NAVY)
        steps = bs.timeline(o)
        # connector lines first, dots on top
        for i in range(3):
            done = steps[i]["state"] == "done"
            c.line([38, DOT_Y[i] + 11, 38, DOT_Y[i + 1] - 11 if i < 2 else CARD_Y[2] + 82],
                   C.GREEN if done else C.BORDER, 2)
        for i, st in enumerate(steps):
            cy, state = DOT_Y[i], st["state"]
            if o["cancelled"]:
                state = "pending"
            if state == "done":
                c.oval(38, cy, 11, fill=C.GREEN)
            elif state == "active":
                c.oval(38, cy, 11, fill=C.BLUE)
            else:
                c.oval(38, cy, 11, fill=C.WHITE, outline=C.BORDER, width=2)
            y = CARD_Y[i]
            active = state == "active"
            c.rrect(70, y, 340, 66, 13, fill=C.PALE if active else C.WHITE, outline=C.BLUE if active else C.BORDER,
                    width=1.5 if active else 1)
            icon_col = C.GREEN if state == "done" else (C.BLUE if active else C.MUTED)
            c.icon(st["icon"], 95, y + 33, 22, icon_col, w=1.4)
            c.text(117, y + 24, st["title"], 16, fill=C.NAVY)
            c.text(117, y + 45, st["sub"], 12, fill=C.BLUE if active else C.MUTED)
        # simulation controls
        if o["cancelled"]:
            c.text(215, 770, "This order was cancelled.", 14, "bold", C.DANGER, "center")
        elif o["stage"] == 4:
            c.text(215, 770, "Delivered — thanks for using Laundry Pal!", 14, "bold", C.GREEN, "center")
        else:
            w = 250 if o["stage"] == 0 else 390
            c.button(20, 726, w, 44, "Simulate next stage  ›", self.next_stage, kind="outline", size=14, r=12)
            if o["stage"] == 0:
                c.button(282, 726, 128, 44, "Cancel order", self.cancel, kind="danger", size=14, r=12)
            c.text(215, 790, "Demo only: there is no live GPS tracking.", 11, fill=C.FAINT, anchor="center")
        # pickup partner
        c.rrect(20, 818, 390, 74, 14, fill=C.WHITE, outline=C.BORDER)
        c.oval(56, 855, 22, fill=C.GREEN_PALE)
        c.text(92, 846, f"{o['partner']} · Pickup partner", 15, "bold", C.NAVY)
        c.text(92, 868, "Need help with this order?", 12, fill=C.MUTED)
        t = c.new_tag()
        c.oval(373, 855, 23, fill=C.GREEN, tags=(t,))
        c.icon("phone", 373, 855, 22, C.WHITE, tags=(t,), w=1.5)
        c.on(t, lambda: c.toast(f"Calling {o['partner']}… (demo)"))

    def next_stage(self):
        o = bs.advance(self.order)
        names = ["", "Picked up", "Washing complete — ironing", "Ironing complete — out for delivery", "Delivered"]
        self.redraw()
        self.c.toast(f"Status updated: {names[o['stage']] if o['stage'] < 5 else ''}")

    def cancel(self):
        bs.cancel(self.order)
        self.redraw()
        self.c.toast("Order cancelled.")
