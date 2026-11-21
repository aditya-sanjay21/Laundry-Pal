"""Screen 7 - Account / Profile (edit profile, manage addresses, sign out)."""
import config
import database as db
from components import images, sheets
from config import C
from screens.base import Screen
from services import booking_service as bs
from services import validation as val


class ProfileScreen(Screen):
    nav_tab = "profile"

    def build(self):
        c, app = self.c, self.app
        user = db.get_user(app.session.user["id"])
        app.session.user = user
        c.header("Account", right=("Edit", self.edit_sheet))
        c.oval(215, 180, 42, fill=C.WHITE, outline=C.BORDER)
        c.photo(175, 140, images.load(user["photo"], 80, 80, circle=True))
        c.text(215, 247, user["name"], 24, "bold", C.NAVY, "center")
        c.text(215, 281, f"{user['email']} · {val.pretty_phone(user['phone'])}", 14, fill=C.MUTED, anchor="center")
        # orders summary
        c.text(20, 320, "My Orders", 20, fill=C.NAVY)
        c.link(410, 320, "View all", lambda: app.tab("orders"), 14)
        c.rrect(20, 342, 390, 111, 16, fill=C.WHITE, outline=C.BORDER)
        nums = db.counters(user["id"])
        for i, (icon, label) in enumerate((("washer", "Current"), ("box", "Picked up"),
                                           ("check_circle", "Delivered"), ("cross_circle", "Cancelled"))):
            cx = 75 + i * 93.5
            c.rrect(cx - 20, 355, 40, 40, 12, fill=C.PALE)
            c.icon(icon, cx, 375, 21, C.BLUE, w=1.4)
            c.text(cx, 411, str(nums[i]), 17, "bold", C.NAVY, "center")
            c.text(cx, 435, label, 12, fill=C.MUTED, anchor="center")
        # address
        c.text(20, 486, "Address", 20, fill=C.NAVY)
        c.link(410, 486, "Manage", self.manage_addresses, 14)
        a = db.default_address(user["id"])
        t = c.new_tag()
        c.rrect(20, 508, 390, 86, 16, fill=C.WHITE, outline=C.BORDER, tags=(t,))
        c.rrect(36, 528, 42, 42, 12, fill=C.GREEN_PALE, tags=(t,))
        c.icon("home", 57, 549, 22, C.GREEN, tags=(t,), w=1.4)
        if a:
            c.text(92, 532, a["label"], 15, "bold", C.NAVY, tags=(t,))
            c.create_text(config.sc(92), config.sc(545), text=bs.full_address(a), anchor="nw",
                          font=c.font(13), fill=C.MUTED, width=config.sc(268), tags=(t,))
        else:
            c.text(92, 549, "Add your first address", 15, fill=C.BLUE, tags=(t,))
        c.icon("chevron_r", 394, 551, 16, C.MUTED, tags=(t,), w=1.4)
        c.on(t, self.manage_addresses)
        c.line([20, 614, 410, 614], C.BORDER, 1)
        # sign out
        so = c.new_tag()
        c.rrect(20, 636, 390, 50, 14, fill=C.DANGER_BG, outline=C.DANGER_BORDER, tags=(so,))
        c.icon("signout", 172, 661, 20, C.DANGER, tags=(so,), w=1.6)
        c.text(197, 661, "Sign Out", 16, "bold", C.DANGER, tags=(so,))
        c.on(so, self.sign_out)

    # ------------------------------------------------------------ actions
    def sign_out(self):
        self.app.logout()

    def manage_addresses(self):
        uid = self.app.session.user["id"]
        sheets.address_picker(self.c, uid, None, lambda aid: None, self.redraw, manage=True)

    def edit_sheet(self):
        c, user = self.c, self.app.session.user
        top = c.open_sheet("Edit profile", 430)
        y, f = top + 70, {}
        for key, ph, icon, text in (("name", "Full name", "profile", user["name"]), ("email", "Email", "mail", user["email"]),
                                    ("phone", "Mobile number", "phone", val.pretty_phone(user["phone"]))):
            f[key] = c.field(24, y, config.W - 48, 52, ph, icon, group="ov", text=text, size=15, r=14)
            y += 62
        err = c.text(24, y + 6, "", 12, fill=C.DANGER, tags=("ov",))

        def save():
            v = {k: e.value() for k, e in f.items()}
            phone = val.phone_digits(v["phone"])
            if len(v["name"]) < 2:
                return c.itemconfig(err, text="Please enter your name.")
            if not val.is_email(v["email"]):
                return c.itemconfig(err, text="Enter a valid email address.")
            if not phone:
                return c.itemconfig(err, text="Enter a valid 10-digit mobile number.")
            try:
                self.app.session.user = db.update_user(user["id"], v["name"].title(), v["email"], phone)
            except ValueError as ex:
                return c.itemconfig(err, text=str(ex))
            c.close_sheet()
            self.redraw()
            c.toast("Profile updated.")

        c.button(24, config.H - 86, config.W - 48, 54, "Save changes", save, tags=("ov",))
