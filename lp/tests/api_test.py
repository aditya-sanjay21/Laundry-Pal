import os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
os.environ["LP_DB"] = os.path.join(tempfile.mkdtemp(), "t.db")
import app as A
c = A.app.test_client()
def call(m, url, tok=None, **j):
    r = getattr(c, m)(url, json=j or None, headers={"Authorization": f"Bearer {tok}"} if tok else {})
    return r.status_code, r.get_json()
ok = lambda cond, msg: print(("PASS " if cond else "FAIL ") + msg) or (cond or sys.exit(1))
s, d = call("post", "/api/auth/login", identifier="rahul.sharma@email.com", password="demo123"); ok(s == 200, "login"); t = d["token"]
s, d = call("post", "/api/auth/signup", name="Ananya Rao", email="ananya@email.com", phone="9123456780", password="secret1"); ok(s == 201, "signup")
s, d = call("get", "/api/providers?sort=price"); ok(s == 200 and d[0]["review_count"] >= 10, "providers with review counts")
ok({p["name"]: p["rating"] for p in d}["FreshFold Laundry"] == 4.9, "rating = average of reviews")
s, d = call("get", "/api/providers/1/reviews"); ok(s == 200 and len(d) == 10, "provider reviews")
s, addr = call("get", "/api/addresses", t)
s, o = call("post", "/api/orders", t, provider_id=1, service="laundry", weight=3, day="Today", slot="Morning (8–11 AM)", address_id=addr[0]["id"], payment="upi")
ok(s == 201 and o["payment_status"] == "pending", "order created as pending"); oid = o["id"]
s, d = call("post", f"/api/orders/{oid}/advance", t); ok(s == 409, "cannot advance an unpaid order")
s, d = call("post", f"/api/orders/{oid}/payment", t, payment="upi", simulate_fail=True); ok(s == 402 and d["order"]["payment_status"] == "failed", "failed payment")
s, d = call("post", f"/api/orders/{oid}/payment", t, payment="card"); ok(s == 200 and d["payment_status"] == "paid", "retry succeeds")
s, d = call("put", f"/api/orders/{oid}", t, day="Tomorrow", slot="Evening (4–7 PM)"); ok(s == 200 and d["pickup_day"] == "Tomorrow", "reschedule")
s, d = call("post", f"/api/orders/{oid}/review", t, rating=5); ok(s == 409, "no review before delivery")
for _ in range(4): call("post", f"/api/orders/{oid}/advance", t)
s, d = call("put", f"/api/orders/{oid}", t, day="Today", slot="Morning (8–11 AM)"); ok(s == 409, "no reschedule after pickup")
s, d = call("post", f"/api/orders/{oid}/cancel", t); ok(s == 409, "no cancel after pickup")
s, d = call("post", f"/api/orders/{oid}/review", t, rating=4, comment="Good"); ok(s == 201 and d["reviewed"], "review delivered order")
s, d = call("post", f"/api/orders/{oid}/review", t, rating=4); ok(s == 409, "one review per order")
s, d = call("get", "/api/me", t); ok(d["counters"]["delivered"] == 13, "counters")
print("All API checks passed")
