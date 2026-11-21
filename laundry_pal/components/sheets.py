"""Bottom sheets that are shared by more than one screen (address picker/editor)."""
import config
import database as db
from config import C
from services import booking_service as bs
from services import validation as val


def address_form(surface, user_id, on_saved):
    """Sheet with fields to add a new address."""
    top = surface.open_sheet("Add address", 560)
    fields = {}
    y = top + 68
    for key, ph in (("label", "Label (Home, Work…)"), ("street", "House no. & street"), ("area", "Area / locality"),
                    ("city", "City"), ("pincode", "Pincode (6 digits)")):
        fields[key] = surface.field(24, y, config.W - 48, 50, ph, group="ov", size=15, r=14)
        y += 60
    fields["city"].set("Bengaluru")
    err = surface.text(24, y + 8, "", 12, fill=C.DANGER, tags=("ov",))

    def save():
        v = {k: e.value() for k, e in fields.items()}
        if not all(v.values()):
            return surface.itemconfig(err, text="Please fill in every field.")
        if not val.is_pincode(v["pincode"]):
            return surface.itemconfig(err, text="Pincode must be exactly 6 digits.")
        aid = db.add_address(user_id, v["label"].title(), v["street"], v["area"], v["city"], v["pincode"])
        surface.close_sheet()
        on_saved(aid)

    surface.button(24, config.H - 86, config.W - 48, 54, "Save address", save, tags=("ov",))


def address_picker(surface, user_id, selected_id, on_pick, on_changed, manage=False):
    """Sheet that lists saved addresses.  manage=True adds 'make default' and delete actions."""
    rows = db.addresses(user_id)
    height = min(640, 190 + max(1, len(rows)) * 82)
    top = surface.open_sheet("Manage addresses" if manage else "Choose pickup address", height)
    y = top + 70
    if not rows:
        surface.text(24, y + 20, "No saved addresses yet.", 15, fill=C.MUTED, tags=("ov",))
    for a in rows:
        sel = a["id"] == selected_id or (manage and a["is_default"])
        t = surface.new_tag()
        surface.rrect(24, y, config.W - 48, 70, 14, fill=C.PALE if sel else C.WHITE,
                      outline=C.BLUE if sel else C.BORDER, tags=("ov", t))
        surface.text(40, y + 22, a["label"] + ("  ·  Default" if a["is_default"] else ""), 15, "bold", C.NAVY, tags=("ov", t))
        surface.text(40, y + 46, bs.short_address(a), 12, fill=C.MUTED, tags=("ov", t), width=260)
        if manage:
            d = surface.new_tag()
            surface.icon("trash", config.W - 54, y + 35, 20, C.DANGER, tags=("ov", d))
            surface.on(d, lambda i=a["id"]: (db.delete_address(user_id, i), on_changed(), address_picker(
                surface, user_id, selected_id, on_pick, on_changed, True)))
            surface.on(t, lambda i=a["id"]: (db.set_default_address(user_id, i), on_changed(), address_picker(
                surface, user_id, selected_id, on_pick, on_changed, True)))
        else:
            surface.on(t, lambda i=a["id"]: (surface.close_sheet(), on_pick(i)))
        y += 82
    surface.button(24, y + 4, config.W - 48, 50, "+  Add new address", lambda: address_form(
        surface, user_id, lambda aid: (on_changed(), on_pick(aid) if not manage else address_picker(
            surface, user_id, selected_id, on_pick, on_changed, True))), kind="outline", size=15, tags=("ov",))
