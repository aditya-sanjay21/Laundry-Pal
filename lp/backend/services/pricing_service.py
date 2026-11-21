
import math

DAYS = ["Today", "Tomorrow"]
SLOTS = ["Morning (8–11 AM)", "Afternoon (12–3 PM)", "Evening (4–7 PM)"]
MIN_KG, MAX_KG = 1, 25

PAYMENTS = [  # key, title, subtitle, icon
    ("upi", "UPI", "Google Pay, PhonePe or UPI ID", "upi"),
    ("card", "Card", "Credit or debit card", "card"),
    ("wallet", "Wallet", "Paytm wallet", "wallet"),
    ("more", "More payment method", "Net banking or cash", "dots"),
]
PAYMENT_LABEL = {"upi": "UPI", "card": "Card", "wallet": "Wallet", "more": "Net banking / Cash"}


def money(n):
    return f"₹{int(round(n)):,}"


def unit_price(provider, service):
    return int(round(provider["price_per_kg"] * service["multiplier"]))


def min_kg_for(provider, service):
    return max(MIN_KG, math.ceil(provider["min_order"] / unit_price(provider, service)))


def default_weight(provider, service):
    return max(3, min_kg_for(provider, service))


def quote(provider, service, weight):
    unit = unit_price(provider, service)
    subtotal = unit * weight
    free = provider["delivery_fee"] == 0 or subtotal >= provider["free_above"]
    delivery = 0 if free else provider["delivery_fee"]
    error = None
    if weight < MIN_KG or weight > MAX_KG:
        error = f"Weight must be between {MIN_KG} and {MAX_KG} kg."
    elif subtotal < provider["min_order"]:
        error = (f"Minimum order is {money(provider['min_order'])}. "
                 f"Please book at least {min_kg_for(provider, service)} kg.")
    return {"unit": unit, "subtotal": subtotal, "delivery": delivery,
            "total": subtotal + delivery, "error": error}
