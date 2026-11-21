"""End-to-end smoke test that drives the real GUI code (no mouse needed).
Run:  python tests/test_journey.py      (on a headless Linux box: xvfb-run python tests/test_journey.py)"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config  # noqa: E402
import database as db  # noqa: E402
from app import App  # noqa: E402
from services import booking_service as bs  # noqa: E402
from services import pricing_service as pr  # noqa: E402

config.DB_PATH = os.path.join(os.environ.get("TMPDIR", "/tmp"), "lp_test.db")
if os.path.exists(config.DB_PATH):
    os.remove(config.DB_PATH)


def ok(cond, msg):
    print(("PASS  " if cond else "FAIL  ") + msg)
    if not cond:
        sys.exit(1)


app = App()
pump = lambda: (app.update_idletasks(), app.update())

# --- login validation + success
s = app.screen
s.id_e.set("bad"); s.pw_e.set("x"); s.submit()
ok(app.session.user is None, "invalid login rejected")
s.id_e.set("aarav.sharma@email.com"); s.pw_e.set("wrongpass"); s.submit()
ok(app.session.user is None, "wrong password rejected")
s.id_e.set("+91 98765 43210"); s.pw_e.set("demo123"); s.submit()
ok(app.session.user and app.current[0] == "home", "demo login (by phone) works")

# --- search + providers filter/sort
app.screen.search.set("blue"); app.screen.do_search()
ok(app.current[0] == "providers" and [p["name"] for p in app.screen.visible(app.service())] == ["Blue Basket Care"], "search narrows providers")
app.session.query = ""; app.session.filters["rating"] = 4.8
ok(len(app.screen.visible(app.service())) == 2, "rating filter")
app.session.filters["rating"] = None; app.session.sort = "price"
ok([p["price_per_kg"] for p in app.screen.visible(app.service())] == [69, 79, 89], "sort by price")
app.screen.filter_sheet(); app.screen.sort_sheet(); pump(); app.screen.c.close_sheet()

# --- booking journey
app.session.provider_id = 1; app.go("details"); app.screen.book()
ok(app.current[0] == "checkout" and app.screen.q["total"] == 237, "checkout total = ₹237")
app.screen.change_weight  # sheet functions exist
app.screen.booking_sheet(); app.screen.change_weight(1); pump()
ok(app.session.booking["weight"] == 4, "weight stepper")
app.screen.done_booking(); ok(app.screen.q["total"] == 316, "total recalculated for 4 kg")
app.screen.pay_var.set("card"); ok(app.session.booking["payment"] == "card", "payment radio updates state")
before = len(db.orders(1))
app.screen.place_order()
for _ in range(60):
    pump(); app.after(60); 
    import time; time.sleep(0.05)
    if app.current[0] == "tracking":
        break
ok(app.current[0] == "tracking" and len(db.orders(1)) == before + 1, "order created, tracking opened")
o = db.latest_order(1)
ok(o["code"] == "LP-20482" and o["total"] == 316 and o["payment_method"] == "Card" and o["stage"] == 0, "order row stored correctly")

# --- tracking progress + cancel rules
for expect in (1, 2, 3, 4):
    app.screen.next_stage(); ok(db.order(o["id"])["stage"] == expect, f"stage -> {expect}")
ok(db.order(o["id"])["stage"] == 4 and not bs.cancel(db.order(o["id"]))["cancelled"], "delivered order cannot be cancelled")

# --- profile: counters, edit, addresses, logout
app.tab("profile"); ok(db.counters(1) == [1, 2, 13, 0], "counters updated after delivery")
app.screen.edit_sheet(); pump(); app.screen.c.close_sheet()
db.update_user(1, "Aarav S", "aarav.sharma@email.com", "9876543210"); app.screen.redraw()
aid = db.add_address(1, "Parents", "5, 3rd Cross", "Jayanagar", "Bengaluru", "560011")
db.set_default_address(1, aid); ok(db.default_address(1)["label"] == "Parents", "address add + make default")
db.delete_address(1, aid); ok(db.default_address(1) is not None, "delete default address promotes another")
app.screen.manage_addresses(); pump(); app.screen.c.close_sheet()
app.tab("orders"); pump()
app.screen = app.screen
app.logout(); ok(app.current[0] == "login" and app.session.user is None, "logout")

# --- sign-up
app.go("signup"); f = app.screen.f
f["name"].set("test user"); f["email"].set("t@x.com"); f["phone"].set("9123456780"); f["pw"].set("secret1"); f["pw2"].set("secret1")
app.screen.submit(); ok(app.session.user and app.session.user["name"] == "Test User", "sign-up creates user and logs in")
app.go("checkout") if False else None

# --- pricing rules
sp = db.provider(2); lau = db.service("laundry")
ok(pr.quote(sp, lau, 3)["delivery"] == 40 and pr.quote(sp, lau, 4)["delivery"] == 0, "delivery fee waived above threshold")
ok(pr.quote(db.provider(1), db.service("ironing"), 2)["error"] is not None, "minimum order validated")
print("\nALL TESTS PASSED")
app.destroy()
