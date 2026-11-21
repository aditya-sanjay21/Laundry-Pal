
import os
import threading
from functools import wraps

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

import database as db
from services import booking_service as bs
from services import pricing_service as pr
from services import validation as val

BASE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(BASE, "..", "frontend", "dist")
DB_PATH = os.environ.get("LP_DB", os.path.join(BASE, "laundry_pal.db"))

app = Flask(__name__, static_folder=None)
app.config["SECRET_KEY"] = os.environ.get("LP_SECRET", "laundry-pal-dev-secret-change-me")
CORS(app)                                    # lets the Vite dev server (port 5173) call this API

signer = URLSafeTimedSerializer(app.config["SECRET_KEY"])



db_lock = threading.RLock()          


@app.before_request
def _open_db():
    db_lock.acquire()
    request.environ["lp_locked"] = True
    if db.conn is None:
        db.connect(DB_PATH)


@app.teardown_request
def _release_db(_exc):
    if request.environ.pop("lp_locked", False):
        db_lock.release()


def err(message, code=400):
    return jsonify({"error": message}), code


def public_user(u):
    return {"id": u["id"], "name": u["name"], "email": u["email"], "phone": u["phone"],
            "phone_pretty": val.pretty_phone(u["phone"]), "photo": u["photo"]}


def make_token(user):
    return signer.dumps({"uid": user["id"]})


def login_required(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        header = request.headers.get("Authorization", "")
        token = header[7:] if header.startswith("Bearer ") else ""
        try:
            uid = signer.loads(token, max_age=60 * 60 * 24 * 7)["uid"]
        except (BadSignature, SignatureExpired):
            return err("Please log in again.", 401)
        user = db.get_user(uid)
        if not user:
            return err("Account not found.", 401)
        request.user = user
        return fn(*a, **kw)
    return wrapper


def provider_json(p, service):
    return {**p, "unit_price": pr.unit_price(p, service), "pickup_text": bs.fmt_pickup_wait(p["pickup_min"]),
            "min_kg": pr.min_kg_for(p, service), "default_weight": pr.default_weight(p, service)}


def address_json(a):
    return {**a, "short": bs.short_address(a), "full": bs.full_address(a)}


def order_json(o, detail=False):
    service, provider = db.service(o["service_key"]), db.provider(o["provider_id"])
    out = {"id": o["id"], "code": o["code"], "service": service["name"], "service_label": service["label"],
           "provider": provider["name"], "weight": o["weight"], "total": o["total"], "service_cost": o["service_cost"],
           "delivery_fee": o["delivery_fee"], "payment_method": o["payment_method"], "stage": o["stage"],
           "cancelled": bool(o["cancelled"]), "status": bs.status_label(o), "created_text": bs.fmt_dt(o["created_at"]),
           "address": o["address_text"], "partner": o["partner"], "partner_phone": o.get("partner_phone"),
           "pickup_day": o["pickup_day"], "pickup_slot": o["pickup_slot"], "provider_id": o["provider_id"],
           "payment_status": o.get("payment_status") or "paid", "reviewed": bool(db.review_for_order(o["id"])),
           "eta_text": "Cancelled" if o["cancelled"] else ("Delivered" if o["stage"] == 4 else bs.fmt_dt(o["eta"]))}
    if detail:
        out["timeline"] = bs.timeline(o)
    return out


@app.post("/api/auth/login")
def login():
    d = request.get_json(silent=True) or {}
    ident, pw = (d.get("identifier") or "").strip(), d.get("password") or ""
    if not ident:
        return err("Enter your email or phone number.")
    if not (val.is_email(ident) or val.phone_digits(ident)):
        return err("That doesn't look like an email or phone.")
    if len(pw) < 6:
        return err("Password must be at least 6 characters.")
    user = db.authenticate(ident, pw)
    if not user:
        return err("Incorrect email/phone or password.", 401)
    return jsonify({"token": make_token(user), "user": public_user(user)})


@app.post("/api/auth/signup")
def signup():
    d = request.get_json(silent=True) or {}
    name, email, pw = (d.get("name") or "").strip(), (d.get("email") or "").strip(), d.get("password") or ""
    phone = val.phone_digits(d.get("phone") or "")
    if len(name) < 2:
        return err("Please enter your full name.")
    if not val.is_email(email):
        return err("Enter a valid email address.")
    if not phone:
        return err("Enter a valid 10-digit mobile number.")
    if len(pw) < 6:
        return err("Password must be at least 6 characters.")
    try:
        user = db.create_user(name.title(), email, phone, pw)
    except ValueError as ex:
        return err(str(ex), 409)
    return jsonify({"token": make_token(user), "user": public_user(user)}), 201



@app.get("/api/me")
@login_required
def me():
    u = request.user
    a = db.default_address(u["id"])
    return jsonify({"user": public_user(u), "counters": dict(zip(("current", "picked", "delivered", "cancelled"),
                    db.counters(u["id"]))), "default_address": address_json(a) if a else None})


@app.put("/api/me")
@login_required
def update_me():
    d = request.get_json(silent=True) or {}
    name, email, phone = (d.get("name") or "").strip(), (d.get("email") or "").strip(), val.phone_digits(d.get("phone") or "")
    if len(name) < 2:
        return err("Please enter your name.")
    if not val.is_email(email):
        return err("Enter a valid email address.")
    if not phone:
        return err("Enter a valid 10-digit mobile number.")
    try:
        user = db.update_user(request.user["id"], name.title(), email, phone)
    except ValueError as ex:
        return err(str(ex), 409)
    return jsonify({"user": public_user(user)})


@app.get("/api/addresses")
@login_required
def list_addresses():
    return jsonify([address_json(a) for a in db.addresses(request.user["id"])])


@app.post("/api/addresses")
@login_required
def add_address():
    d = request.get_json(silent=True) or {}
    v = {k: (d.get(k) or "").strip() for k in ("label", "street", "area", "city", "pincode")}
    if not all(v.values()):
        return err("Please fill in every field.")
    if not val.is_pincode(v["pincode"]):
        return err("Pincode must be exactly 6 digits.")
    aid = db.add_address(request.user["id"], v["label"].title(), v["street"], v["area"], v["city"], v["pincode"],
                         bool(d.get("make_default")))
    return jsonify({"id": aid}), 201


@app.put("/api/addresses/<int:aid>/default")
@login_required
def default_address(aid):
    db.set_default_address(request.user["id"], aid)
    return jsonify({"ok": True})


@app.delete("/api/addresses/<int:aid>")
@login_required
def delete_address(aid):
    db.delete_address(request.user["id"], aid)
    return jsonify({"ok": True})


@app.get("/api/services")
def services():
    return jsonify(db.services())


@app.get("/api/providers")
def providers():
    service = db.service(request.args.get("service", "laundry")) or db.service("laundry")
    rows = db.providers()
    q = request.args.get("q", "").strip().lower()
    if q:
        rows = [p for p in rows if q in p["name"].lower()]
    for key, field, op in (("rating", "rating", "ge"), ("price", "price_per_kg", "le"), ("pickup", "pickup_min", "le")):
        raw = request.args.get(key)
        if raw:
            try:
                limit = float(raw)
            except ValueError:
                return err(f"Bad {key} filter.")
            rows = [p for p in rows if (p[field] >= limit if op == "ge" else p[field] <= limit)]
    keys = {"rating": lambda p: -p["rating"], "price": lambda p: p["price_per_kg"],
            "distance": lambda p: p["distance_km"], "pickup": lambda p: p["pickup_min"]}
    rows = sorted(rows, key=keys.get(request.args.get("sort", "rating"), keys["rating"]))
    return jsonify([provider_json(p, service) for p in rows])


@app.get("/api/providers/<int:pid>")
def provider_detail(pid):
    service = db.service(request.args.get("service", "laundry")) or db.service("laundry")
    p = db.provider(pid)
    if not p:
        return err("Provider not found.", 404)
    return jsonify({"provider": provider_json(p, service), "service": service})


@app.get("/api/providers/<int:pid>/reviews")
def provider_reviews(pid):
    if not db.provider(pid):
        return err("Provider not found.", 404)
    return jsonify(db.provider_reviews(pid))


@app.post("/api/quote")
def quote():
    d = request.get_json(silent=True) or {}
    p, s = db.provider(d.get("provider_id") or 0), db.service(d.get("service") or "")
    if not p or not s:
        return err("Unknown provider or service.", 404)
    try:
        weight = int(d.get("weight"))
    except (TypeError, ValueError):
        return err("Weight must be a whole number of kg.")
    return jsonify(pr.quote(p, s, weight))



@app.post("/api/orders")
@login_required
def create_order():
    d = request.get_json(silent=True) or {}
    p, s = db.provider(d.get("provider_id") or 0), db.service(d.get("service") or "")
    if not p or not s:
        return err("Unknown provider or service.", 404)
    try:
        weight = int(d.get("weight"))
    except (TypeError, ValueError):
        return err("Weight must be a whole number of kg.")
    day, slot, pay = d.get("day"), d.get("slot"), d.get("payment")
    if day not in pr.DAYS or slot not in pr.SLOTS or pay not in pr.PAYMENT_LABEL:
        return err("Invalid pickup day, slot or payment method.")
    addr = next((a for a in db.addresses(request.user["id"]) if a["id"] == d.get("address_id")), None)
    oid, error = bs.place_order(request.user, p, s, weight, day, slot, addr, pay)   # payment is simulated
    if error:
        return err(error)
    return jsonify(order_json(db.order(oid), True)), 201      


@app.get("/api/orders")
@login_required
def list_orders():
    return jsonify([order_json(o) for o in db.orders(request.user["id"])])


def _own_order(oid):
    o = db.order(oid)
    return o if o and o["user_id"] == request.user["id"] else None


@app.get("/api/orders/<int:oid>")
@login_required
def get_order(oid):
    o = _own_order(oid)
    return jsonify(order_json(o, True)) if o else err("Order not found.", 404)


@app.get("/api/orders/latest")
@login_required
def latest_order():
    o = db.latest_order(request.user["id"])
    return jsonify(order_json(o, True)) if o else err("No orders yet.", 404)


@app.post("/api/orders/<int:oid>/advance")
@login_required
def advance_order(oid):
    """Simulation only: stands in for the provider / pickup partner updating the status."""
    o = _own_order(oid)
    if not o:
        return err("Order not found.", 404)
    if o["payment_status"] != "paid":
        return err("Complete the payment first.", 409)
    return jsonify(order_json(bs.advance(o), True))


@app.put("/api/orders/<int:oid>")
@login_required
def reschedule_order(oid):
    o = _own_order(oid)
    if not o:
        return err("Order not found.", 404)
    d = request.get_json(silent=True) or {}
    if d.get("day") not in pr.DAYS or d.get("slot") not in pr.SLOTS:
        return err("Choose a valid pickup day and time slot.")
    if o["stage"] != 0 or o["cancelled"]:
        return err("Only orders waiting for pickup can be rescheduled.", 409)
    return jsonify(order_json(bs.reschedule(o, d["day"], d["slot"]), True))


@app.post("/api/orders/<int:oid>/payment")
@login_required
def pay_order(oid):
    """Simulated payment (first attempt or a retry). Send simulate_fail=true to demo a failed payment."""
    o = _own_order(oid)
    if not o:
        return err("Order not found.", 404)
    d = request.get_json(silent=True) or {}
    key = d.get("payment")
    if key not in pr.PAYMENT_LABEL:
        return err("Choose a payment method.")
    if o["cancelled"] or o["payment_status"] == "paid":
        return err("This order does not need a payment.", 409)
    o = bs.pay(o, key, bool(d.get("simulate_fail")))
    if o["payment_status"] == "failed":
        return jsonify({"error": "Payment failed. Please retry or choose another method.",
                        "order": order_json(o, True)}), 402
    return jsonify(order_json(o, True))


@app.post("/api/orders/<int:oid>/review")
@login_required
def review_order(oid):
    o = _own_order(oid)
    if not o:
        return err("Order not found.", 404)
    if o["stage"] != 4 or o["cancelled"]:
        return err("You can review an order after it is delivered.", 409)
    if db.review_for_order(oid):
        return err("You have already reviewed this order.", 409)
    d = request.get_json(silent=True) or {}
    try:
        rating = int(d.get("rating"))
    except (TypeError, ValueError):
        return err("Please choose a rating from 1 to 5.")
    if not 1 <= rating <= 5:
        return err("Please choose a rating from 1 to 5.")
    db.add_review(o, request.user, rating, (d.get("comment") or "").strip()[:300])
    return jsonify(order_json(db.order(oid), True)), 201


@app.post("/api/orders/<int:oid>/cancel")
@login_required
def cancel_order(oid):
    o = _own_order(oid)
    if not o:
        return err("Order not found.", 404)
    if o["stage"] != 0 or o["cancelled"]:
        return err("Only orders waiting for pickup can be cancelled.", 409)
    return jsonify(order_json(bs.cancel(o), True))



@app.get("/images/<path:name>")
def images(name):
    return send_from_directory(os.path.join(BASE, "static", "images"), name)


@app.get("/", defaults={"path": ""})
@app.get("/<path:path>")
def spa(path):
    if path.startswith("api/"):
        return err("Not found.", 404)
    if os.path.isdir(DIST):
        full = os.path.join(DIST, path)
        return send_from_directory(DIST, path if path and os.path.isfile(full) else "index.html")
    return jsonify({"message": "Laundry Pal API is running. Build the React app (npm run build) or run npm run dev."})


if __name__ == "__main__":
    debug_mode = os.environ.get("LP_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)