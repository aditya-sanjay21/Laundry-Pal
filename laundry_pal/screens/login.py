"""Screen 1 - Login (plus the Sign-up screen that shares its style)."""
import database as db
from config import C
from screens.base import Screen
from services import validation as val


def _logo(c, cx, cy):
    c.rrect(cx - 46, cy - 46, 92, 92, 28, fill=C.PALE)
    c.icon("washer", cx - 1, cy + 1, 40, C.BLUE, w=1.1)
    c.oval(cx + 24, cy - 27, 7, fill=C.GREEN_DOT, outline=C.PALE, width=2)


class LoginScreen(Screen):
    def build(self):
        c = self.c
        _logo(c, 215, 150)
        c.text(215, 232, "Laundry Pal", 33, "bold", C.NAVY, "center")
        c.text(215, 265, "Laundry & Ironing, made simple", 15, fill=C.MUTED, anchor="center")
        c.text(28, 430, "Welcome back", 25, fill=C.NAVY)
        c.text(28, 457, "Log in to schedule your next fresh load.", 14, fill=C.MUTED)
        self.id_e = c.field(28, 482, 374, 56, "Email or phone", "mail")
        self.pw_e = c.field(28, 556, 374, 56, "Password", "lock", secret=True)
        self.err = c.text(28, 637, "", 12, fill=C.DANGER)
        c.link(402, 637, "Forgot password?", lambda: c.toast("Password reset is not part of this demo."), 13)
        c.button(28, 661, 374, 56, "Log in", self.submit)
        t = c.new_tag()
        for item in c.text_width_center([("New user? ", "normal", C.MUTED), ("Sign up", "bold", C.BLUE)], 867, 14):
            c.addtag_withtag(t, item)
        c.on(t, lambda: self.app.go("signup"))
        for e in (self.id_e, self.pw_e):
            e.bind("<Return>", lambda _e: self.submit())

    def submit(self):
        c = self.c
        ident, pw = self.id_e.value(), self.pw_e.value()
        for e in (self.id_e, self.pw_e):
            c.mark_error(e, False)
        problem = None
        if not ident:
            problem, bad = "Enter your email or phone number.", self.id_e
        elif not (val.is_email(ident) or val.phone_digits(ident)):
            problem, bad = "That doesn't look like an email or phone.", self.id_e
        elif len(pw) < 6:
            problem, bad = "Password must be at least 6 characters.", self.pw_e
        if problem:
            c.mark_error(bad)
            return c.itemconfig(self.err, text=problem)
        user = db.authenticate(ident, pw)
        if not user:
            c.mark_error(self.pw_e)
            return c.itemconfig(self.err, text="Incorrect email/phone or password.")
        self.app.session.user = user
        self.app.go("home", reset=True)


class SignupScreen(Screen):
    def build(self):
        c = self.c
        t = c.new_tag()
        c.rect(8, 56, 52, 50, fill=C.BG, tags=(t,))
        c.icon("chevron_l", 32, 81, 22, C.NAVY_SOFT, tags=(t,), w=1.5)
        c.on(t, self.app.back)
        c.text(28, 140, "Create account", 28, "bold", C.NAVY)
        c.text(28, 170, "Book fresh laundry in a few taps.", 14, fill=C.MUTED)
        specs = [("name", "Full name", "profile", False), ("email", "Email", "mail", False),
                 ("phone", "Mobile number", "phone", False), ("pw", "Password (min 6 characters)", "lock", True),
                 ("pw2", "Confirm password", "lock", True)]
        self.f, y = {}, 205
        for key, ph, icon, secret in specs:
            self.f[key] = c.field(28, y, 374, 54, ph, icon, secret=secret, size=15)
            y += 66
        self.err = c.text(28, y + 6, "", 12, fill=C.DANGER)
        c.button(28, y + 28, 374, 56, "Sign up", self.submit)
        t2 = c.new_tag()
        for item in c.text_width_center([("Already have an account? ", "normal", C.MUTED), ("Log in", "bold", C.BLUE)], 867, 14):
            c.addtag_withtag(t2, item)
        c.on(t2, self.app.back)

    def submit(self):
        c, v = self.c, {k: e.value() for k, e in self.f.items()}
        for e in self.f.values():
            c.mark_error(e, False)
        phone = val.phone_digits(v["phone"])
        checks = [("name", len(v["name"]) >= 2, "Please enter your full name."),
                  ("email", val.is_email(v["email"]), "Enter a valid email address."),
                  ("phone", bool(phone), "Enter a valid 10-digit mobile number."),
                  ("pw", len(v["pw"]) >= 6, "Password must be at least 6 characters."),
                  ("pw2", v["pw"] == v["pw2"], "Passwords do not match.")]
        for key, ok, msg in checks:
            if not ok:
                c.mark_error(self.f[key])
                return c.itemconfig(self.err, text=msg)
        try:
            user = db.create_user(v["name"].title(), v["email"], phone, v["pw"])
        except ValueError as ex:
            c.mark_error(self.f["email"])
            return c.itemconfig(self.err, text=str(ex))
        self.app.session.user = user
        self.app.go("home", reset=True)
