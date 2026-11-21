"""Screen 5 - Review & Payment (booking sheet, address picker, simulated payment)."""
import tkinter as tk

import config
import database as db
from components import images, sheets
from config import C
from screens.base import Screen
from services import booking_service as bs
from services import pricing_service as pr


class CheckoutScreen(Screen):
    def build(self):
        c, app = self.c, self.app
        if not hasattr(self, "pay_var"):          # one StringVar drives the radio buttons
            self.pay_var = tk.StringVar(value=app.session.booking["payment"])
            self.pay_var.trace_add("write", lambda *_: self.on_pay_change())
        b, p, service = app.session.booking, app.provider(), app.service()
        self.addr = next((a for a in db.addresses(app.session.user["id"]) if a["id"] == b["address_id"]), None)
        self.q = pr.quote(p, service, b["weight"])
        q = self.q

        c.header("Review & Payment", on_back=app.back)
        c.text(20, 137, "Order review", 20, fill=C.NAVY)
        c.rrect(20, 162, 390, 266, 16, fill=C.WHITE, outline=C.BORDER)
        c.rrect(36, 177, 42, 42, 12, fill=C.PALE)
        c.icon("washer", 57, 198, 24, C.BLUE, w=1.4)
        c.text(92, 188, "Service", 12, fill=C.MUTED)
        c.text(92, 208, service["label"], 16, "bold", C.NAVY)
        c.line([36, 234, 394, 234], C.BORDER, 1)
        # address (tap to change)
        t_addr = c.new_tag()
        c.rect(30, 240, 370, 52, fill=C.WHITE, tags=(t_addr,))
        c.icon("pin", 44, 254, 17, C.BLUE, tags=(t_addr,), w=1.3)
        c.text(64, 254, "Pickup address", 12, fill=C.MUTED, tags=(t_addr,))
        c.text(394, 254, "Change", 12, "bold", C.BLUE, "e", tags=(t_addr,))
        c.text(64, 274, bs.short_address(self.addr) if self.addr else "Add a pickup address", 14,
               fill=C.NAVY if self.addr else C.DANGER, tags=(t_addr,))
        c.on(t_addr, self.address_sheet)
        # details row (tap to change)
        t_det = c.new_tag()
        c.rect(30, 290, 370, 26, fill=C.WHITE, tags=(t_det,))
        c.text(36, 302, "Details", 14, fill=C.MUTED, tags=(t_det,))
        c.icon("chevron_r", 386, 302, 14, C.BLUE, tags=(t_det,), w=1.5)
        c.text(374, 302, f"{b['weight']} kg · Pickup {b['day'].lower()}", 14, fill=C.NAVY, anchor="e", tags=(t_det,))
        c.on(t_det, self.booking_sheet)
        c.text(36, 330, "Service cost", 14, fill=C.MUTED)
        c.text(394, 330, pr.money(q["subtotal"]), 14, fill=C.NAVY, anchor="e")
        c.text(36, 358, "Pickup & delivery", 14, fill=C.MUTED)
        c.text(394, 358, "Free" if q["delivery"] == 0 else pr.money(q["delivery"]), 14, fill=C.NAVY, anchor="e")
        c.line([36, 379, 394, 379], C.BORDER, 1)
        c.text(36, 402, "Total", 15, "bold", C.NAVY)
        c.text(394, 402, pr.money(q["total"]), 18, "bold", C.NAVY, "e")
        if q["error"]:
            c.text(36, 420, q["error"], 11, fill=C.DANGER)
        # payment options
        c.text(20, 453, "Payment options", 20, fill=C.NAVY)
        c.rrect(20, 477, 390, 226, 16, fill=C.WHITE, outline=C.BORDER)
        self.radios = {}
        for i, (key, title, sub, icon) in enumerate(pr.PAYMENTS):
            top = 477 + i * 56.5
            cy, t = top + 28, c.new_tag()
            c.rect(24, top + 2, 382, 52, fill=C.WHITE, tags=(t,))
            c.icon(icon, 44, cy, 19, C.BLUE, tags=(t,), w=1.3)
            c.text(65, cy - 9, title, 15, fill=C.NAVY, tags=(t,))
            c.text(65, cy + 10, sub, 11, fill=C.MUTED, tags=(t,))
            ring = c.oval(387, cy, 9, fill=C.WHITE, outline=C.RADIO, width=1.5, tags=(t,))
            dot = c.oval(387, cy, 3.5, fill="", outline="", tags=(t,))
            self.radios[key] = (ring, dot)
            c.on(t, lambda k=key: self.pay_var.set(k))
            if i < 3:
                c.line([20, top + 56.5, 410, top + 56.5], C.BORDER, 1)
        self.paint_radios()
        c.button(20, 838, 390, 56, f"Place Order · {pr.money(q['total'])}", self.place_order)

    # ------------------------------------------------------------ payment radios
    def paint_radios(self):
        for key, (ring, dot) in self.radios.items():
            on = self.pay_var.get() == key
            self.c.itemconfig(ring, fill=C.BLUE if on else C.WHITE, outline=C.BLUE if on else C.RADIO)
            self.c.itemconfig(dot, fill=C.WHITE if on else "", outline="")

    def on_pay_change(self):
        self.app.session.booking["payment"] = self.pay_var.get()
        if self.winfo_exists():
            self.paint_radios()

    # ------------------------------------------------------------ sheets
    def address_sheet(self):
        uid = self.app.session.user["id"]
        sheets.address_picker(self.c, uid, self.app.session.booking["address_id"], self.pick_address,
                              on_changed=lambda: None)

    def pick_address(self, aid):
        self.app.session.booking["address_id"] = aid
        self.redraw()

    def booking_sheet(self):
        c, b = self.c, self.app.session.booking
        p, service = self.app.provider(), self.app.service()
        top = c.open_sheet("Weight & pickup", 520)
        y = top + 78
        c.text(24, y, "Approximate weight", 14, "bold", C.MUTED, tags=("ov",))
        for sym, dx, step in (("minus", 24, -1), ("plus", 238, 1)):
            t = c.new_tag()
            c.rrect(dx, y + 18, 54, 54, 15, fill=C.PALE, tags=("ov", t))
            c.icon(sym, dx + 27, y + 45, 22, C.BLUE, tags=("ov", t), w=2)
            c.on(t, lambda s=step: self.change_weight(s))
        c.text(168, y + 45, f"{b['weight']} kg", 22, "bold", C.NAVY, "center", tags=("ov",))
        q = pr.quote(p, service, b["weight"])
        c.text(24, y + 90, f"{pr.money(q['unit'])} per kg · minimum order {pr.money(p['min_order'])}", 12, fill=C.MUTED, tags=("ov",))
        y += 128
        c.text(24, y, "Pickup day", 14, "bold", C.MUTED, tags=("ov",))
        x = 24
        for d in pr.DAYS:
            x += c.chip(x, y + 18, d, b["day"] == d, lambda d=d: self.set_booking("day", d)) + 8
        y += 86
        c.text(24, y, "Pickup slot", 14, "bold", C.MUTED, tags=("ov",))
        x = 24
        for s in pr.SLOTS:
            label = s.split(" (")[0]
            x += c.chip(x, y + 18, label, b["slot"] == s, lambda s=s: self.set_booking("slot", s)) + 8
        c.text(24, y + 66, b["slot"] or pr.SLOTS[0], 12, fill=C.MUTED, tags=("ov",))
        c.button(24, config.H - 86, config.W - 48, 54, "Done", self.done_booking, tags=("ov",))

    def change_weight(self, step):
        b = self.app.session.booking
        b["weight"] = max(pr.MIN_KG, min(pr.MAX_KG, b["weight"] + step))
        self.booking_sheet()

    def set_booking(self, key, value):
        self.app.session.booking[key] = value
        self.booking_sheet()

    def done_booking(self):
        self.c.close_sheet()
        self.redraw()

    # ------------------------------------------------------------ place order (simulated payment)
    def place_order(self):
        c, app = self.c, self.app
        if not self.addr:
            c.toast("Please add a pickup address first.", error=True)
            return self.address_sheet()
        if self.q["error"]:
            c.toast(self.q["error"], error=True)
            return self.booking_sheet()
        self.show_payment_overlay()

    def show_payment_overlay(self):
        c = self.c
        c.close_sheet()
        c.photo(0, 0, images.dim_layer(150), tags=("ov",))
        c.rrect(65, 330, 300, 250, 24, fill=C.WHITE, tags=("ov",))
        self.spin = c.arc(215, 420, 28, 0, 100, C.BLUE, 5, tags=("ov",))
        self.pay_title = c.text(215, 485, "Processing payment…", 17, "bold", C.NAVY, "center", tags=("ov",))
        pay = pr.PAYMENT_LABEL[self.pay_var.get()]
        self.pay_sub = c.text(215, 512, f"{pr.money(self.q['total'])} via {pay}", 13, fill=C.MUTED, anchor="center", tags=("ov",))
        c.text(215, 548, "Simulated — no real money is charged", 11, fill=C.FAINT, anchor="center", tags=("ov",))
        self.angle, self.frames = 0, 0
        self.animate()

    def animate(self):
        if not self.winfo_exists():
            return
        self.frames += 1
        if self.frames < 28:
            self.angle = (self.angle + 28) % 360
            self.c.itemconfig(self.spin, start=self.angle)
            self.after(50, self.animate)
        else:
            self.finish_payment()

    def finish_payment(self):
        c, app = self.c, self.app
        ses, b = app.session, app.session.booking
        oid, error = bs.place_order(ses.user, app.provider(), app.service(), b["weight"], b["day"],
                                    b["slot"] or pr.SLOTS[0], self.addr, self.pay_var.get())
        if error:
            c.close_sheet()
            return c.toast(error, error=True)
        c.delete(self.spin)
        c.oval(215, 420, 30, fill=C.GREEN, tags=("ov",))
        c.icon("check", 215, 420, 30, C.WHITE, tags=("ov",), w=2.4)
        c.itemconfig(self.pay_title, text="Payment successful")
        c.itemconfig(self.pay_sub, text="Order placed — taking you to tracking…")
        ses.order_id = oid
        self.after(1100, lambda: self.app.go_with_history([("home", {})], "tracking", order_id=oid)
                   if self.winfo_exists() else None)
