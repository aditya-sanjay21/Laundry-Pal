"""Booking logic: creating orders, moving them through the stages, formatting."""
import datetime as dt

import database as db
from services import pricing_service as pr

FMT = db.FMT
STAGES = [("Picked up", "box"), ("Washing", "washer"), ("Ironing", "shirt"), ("Out for delivery", "bike")]
PARTNERS = ["Ravi", "Imran", "Suresh", "Kiran"]


# ----------------------------------------------------------- date formatting
def _parse(s):
    return dt.datetime.strptime(s, FMT) if s else None


def fmt_time(d):
    return d.strftime("%I:%M %p").lstrip("0")


def fmt_dt(s):
    """'2026-10-06 10:20' -> 'Today, 10:20 AM' / 'Tomorrow, ...' / '12 Oct, ...'"""
    d = _parse(s)
    if not d:
        return ""
    diff = (d.date() - dt.date.today()).days
    day = {0: "Today", 1: "Tomorrow", -1: "Yesterday"}.get(diff, d.strftime("%d %b").lstrip("0"))
    return f"{day}, {fmt_time(d)}"


def fmt_pickup_wait(minutes):
    return "Pickup in 1 hr" if minutes == 60 else f"Pickup in {minutes} min"


def short_address(a):
    return f"{a['street']}, {a['area']}, {a['city']}"


def full_address(a):
    return f"{short_address(a)} {a['pincode']}"


# ----------------------------------------------------------- orders
def place_order(user, provider, service, weight, day, slot, address, payment_key):
    """Validates and stores a new order. Returns (order_id, None) or (None, error message)."""
    if not address:
        return None, "Please add a pickup address first."
    q = pr.quote(provider, service, weight)
    if q["error"]:
        return None, q["error"]
    now = dt.datetime.now().replace(second=0, microsecond=0)
    pickup_date = now.date() + dt.timedelta(days=0 if day == "Today" else 1)
    eta = dt.datetime.combine(pickup_date + dt.timedelta(days=1), dt.time(11, 0))
    ready = dt.datetime.combine(pickup_date, dt.time(16, 0))
    code = db.next_order_code()
    oid = db.insert_order(
        code=code, user_id=user["id"], provider_id=provider["id"], service_key=service["key"],
        weight=weight, pickup_day=day, pickup_slot=slot, address_text=short_address(address),
        service_cost=q["subtotal"], delivery_fee=q["delivery"], total=q["total"],
        payment_method=pr.PAYMENT_LABEL[payment_key], stage=0, cancelled=0,
        created_at=now.strftime(FMT), picked_at=None, eta=eta.strftime(FMT),
        ready_by=ready.strftime(FMT), partner=PARTNERS[int(code[3:]) % len(PARTNERS)])
    return oid, None


def advance(order):
    """Simulation helper: move to the next stage. Returns the updated order."""
    if order["cancelled"] or order["stage"] >= 4:
        return order
    stage = order["stage"] + 1
    extra = {"picked_at": dt.datetime.now().strftime(FMT)} if stage == 1 else {}
    db.update_order(order["id"], stage=stage, **extra)
    return db.order(order["id"])


def cancel(order):
    if order["stage"] == 0 and not order["cancelled"]:
        db.update_order(order["id"], cancelled=1)
    return db.order(order["id"])


def status_label(o):
    if o["cancelled"]:
        return "Cancelled"
    return ["Pickup scheduled", "Washing", "Ironing", "Out for delivery", "Delivered"][o["stage"]]


def timeline(o):
    """Returns 4 dicts (title, icon, state, subtitle) for the tracking screen."""
    p, rows = o["stage"], []
    eta = fmt_dt(o["eta"])
    for i, (title, icon) in enumerate(STAGES):
        state = "done" if p > i else ("active" if p == i else "pending")
        if i == 0:
            sub = {"done": fmt_dt(o["picked_at"]), "active": f"Scheduled · {o['pickup_day']}, {o['pickup_slot']}",
                   "pending": "Up next"}[state]
        elif i == 1:
            sub = {"done": "Completed", "active": f"In progress · Ready by {fmt_time(_parse(o['ready_by']))}",
                   "pending": "Up next" if p == 0 else "Pending"}[state]
        elif i == 2:
            sub = {"done": "Completed", "active": "In progress",
                   "pending": "Up next" if p == 1 else "Pending"}[state]
        else:
            sub = {"done": "Delivered", "active": f"On the way · Arriving {eta}",
                   "pending": "Expected " + eta[0].lower() + eta[1:]}[state]
        rows.append({"title": title, "icon": icon, "state": state, "sub": sub})
    return rows
