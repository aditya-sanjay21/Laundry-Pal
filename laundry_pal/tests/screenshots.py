"""Developer helper: opens every screen and saves a PNG of each into ./screenshots.
Needs a display (on a headless Linux box run it with xvfb-run)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PIL import ImageGrab  # noqa: E402

import config  # noqa: E402
import database as db  # noqa: E402
from app import App  # noqa: E402

OUT = os.path.join(config.BASE_DIR, "screenshots")
os.makedirs(OUT, exist_ok=True)


def snap(app, name):
    app.update_idletasks()
    app.update()
    x, y = app.container.winfo_rootx(), app.container.winfo_rooty()
    w, h = app.container.winfo_width(), app.container.winfo_height()
    ImageGrab.grab(bbox=(x, y, x + w, y + h)).save(os.path.join(OUT, name + ".png"))


if __name__ == "__main__":
    config.DB_PATH = "/tmp/lp_shots.db"
    if os.path.exists(config.DB_PATH):
        os.remove(config.DB_PATH)
    app = App()
    snap(app, "01_login")
    app.screen.id_e.set("aarav.sharma@email.com"); app.screen.pw_e.set("demo123"); app.screen.submit()
    snap(app, "02_home")
    app.session.service_key = "laundry"; app.go("providers"); snap(app, "03_providers")
    app.session.provider_id = 1; app.go("details"); snap(app, "04_details")
    app.screen.book(); snap(app, "05_checkout")
    app.go_with_history([("home", {})], "tracking", order_id=db.latest_order(1)["id"]); snap(app, "06_tracking")
    app.tab("profile"); snap(app, "07_profile")
    app.tab("orders"); snap(app, "08_orders")
    app.destroy()
