"""Bottom navigation bar (Home / Orders / Profile)."""
import config
from config import C

TABS = [("home", "Home", "home", 90), ("orders", "Orders", "orders", 215), ("profile", "Profile", "profile", 340)]


def draw(surface, active, on_select):
    surface.rect(0, 838, config.W, config.H - 838, fill=C.WHITE)
    surface.line([0, 838, config.W, 838], C.BORDER, 1)
    for key, label, icon, cx in TABS:
        on = key == active
        col = C.BLUE if on else C.NAVY_SOFT
        t = surface.new_tag()
        surface.rect(cx - 45, 842, 90, 60, fill=C.WHITE, tags=(t,))          # hit area
        surface.icon(icon, cx, 866, 24, col, tags=(t,), w=1.5)
        surface.text(cx, 887, label, 12, "bold" if on else "normal", col, "center", tags=(t,))
        surface.on(t, lambda k=key: on_select(k))
