
import datetime as dt
import hashlib
import secrets
import sqlite3

conn = None
FMT = "%Y-%m-%d %H:%M"


def connect(path):
    global conn
    conn = sqlite3.connect(path, check_same_thread=False)   
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    _create_schema()
    if not _one("SELECT id FROM users LIMIT 1"):
        _seed()
    return conn


def _create_schema():
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, phone TEXT NOT NULL,
        pw_hash TEXT NOT NULL, salt TEXT NOT NULL, photo TEXT);
    CREATE TABLE IF NOT EXISTS addresses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id),
        label TEXT NOT NULL, street TEXT NOT NULL, area TEXT NOT NULL,
        city TEXT NOT NULL, pincode TEXT NOT NULL, is_default INTEGER DEFAULT 0);
    CREATE TABLE IF NOT EXISTS services(
        key TEXT PRIMARY KEY, name TEXT, subtitle TEXT, label TEXT,
        multiplier REAL, image TEXT, sort_order INTEGER);
    CREATE TABLE IF NOT EXISTS providers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, address TEXT, distance_km REAL, rating REAL, pickup_min INTEGER,
        price_per_kg INTEGER, min_order INTEGER, delivery_fee INTEGER, free_above INTEGER,
        details_text TEXT, quality_text TEXT, image_list TEXT, image_hero TEXT);
    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE, user_id INTEGER REFERENCES users(id),
        provider_id INTEGER REFERENCES providers(id), service_key TEXT REFERENCES services(key),
        weight INTEGER, pickup_day TEXT, pickup_slot TEXT, address_text TEXT,
        service_cost INTEGER, delivery_fee INTEGER, total INTEGER,
        payment_method TEXT, stage INTEGER DEFAULT 0, cancelled INTEGER DEFAULT 0,
        created_at TEXT, picked_at TEXT, eta TEXT, ready_by TEXT, partner TEXT,
        partner_phone TEXT, payment_status TEXT DEFAULT 'paid');
    CREATE TABLE IF NOT EXISTS reviews(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER UNIQUE REFERENCES orders(id),
        user_id INTEGER REFERENCES users(id),
        provider_id INTEGER NOT NULL REFERENCES providers(id),
        reviewer_name TEXT, rating INTEGER NOT NULL, comment TEXT, created_at TEXT);
    """)
    # upgrade databases created before Milestone 2 (adds the new order columns)
    cols = [r[1] for r in conn.execute("PRAGMA table_info(orders)")]
    if "partner_phone" not in cols:
        conn.execute("ALTER TABLE orders ADD COLUMN partner_phone TEXT")
    if "payment_status" not in cols:
        conn.execute("ALTER TABLE orders ADD COLUMN payment_status TEXT DEFAULT 'paid'")
    conn.commit()


def _hash(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()


def _seed():
   
    for row in [
        ("laundry", "Laundry", "Wash & fold", "Laundry · Wash & Fold", 1.0, "service_laundry.jpg", 1),
        ("ironing", "Ironing", "Crisp & ready", "Ironing · Crisp & Ready", 0.7, "service_ironing.jpg", 2),
        ("dryclean", "Dry Clean", "Care for special fabrics", "Dry Clean · Special Fabrics", 2.2,
         "service_dryclean.jpg", 3)]:
        conn.execute("INSERT INTO services VALUES(?,?,?,?,?,?,?)", row)
    
    for row in [
        ("FreshFold Laundry", "12th Main Road", 0.8, 4.9, 30, 79, 199, 0, 0,
         "Pickup today · Ready in 24 hours", "Hygienic wash · Free pickup & delivery",
         "provider_freshfold.jpg", "provider_freshfold_hero.jpg"),
        ("Sparkle Wash Co.", "100 Feet Road", 1.5, 4.8, 45, 89, 249, 40, 300,
         "Pickup today · Ready in 24 hours", "Eco detergents · Free pickup above ₹300",
         "provider_sparkle.jpg", None),
        ("Blue Basket Care", "CMH Road", 1.2, 4.7, 60, 69, 149, 30, 250,
         "Pickup today · Ready in 36 hours", "Machine care · Free pickup above ₹250",
         "provider_bluebasket.jpg", None)]:
        conn.execute("INSERT INTO providers(name,address,distance_km,rating,pickup_min,price_per_kg,"
                     "min_order,delivery_fee,free_above,details_text,quality_text,image_list,image_hero)"
                     " VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", row)
    
    salt = secrets.token_hex(8)
    conn.execute("INSERT INTO users(name,email,phone,pw_hash,salt,photo) VALUES(?,?,?,?,?,?)",
                 ("Rahul Sharma", "rahul.sharma@email.com", "9876543210",
                  _hash("demo123", salt), salt, "profile_aarav.jpg"))
    conn.execute("INSERT INTO addresses(user_id,label,street,area,city,pincode,is_default) VALUES"
                 "(1,'Home','24, 12th Main Road','Indiranagar','Bengaluru','560038',1)")
    conn.execute("INSERT INTO addresses(user_id,label,street,area,city,pincode,is_default) VALUES"
                 "(1,'Work','7, CMH Road','Indiranagar','Bengaluru','560038',0)")
    
    now = dt.datetime.now().replace(second=0, microsecond=0)
    today = now.replace(hour=0, minute=0)
    f = lambda d: d.strftime(FMT)
    addr = "24, 12th Main Road, Indiranagar, Bengaluru"
    n = 20467
    for i in range(12):                       # 12 delivered orders
        created = today - dt.timedelta(days=30 - i * 2) + dt.timedelta(hours=10)
        w = 3 + i % 4
        cost = 79 * w
        conn.execute("INSERT INTO orders(code,user_id,provider_id,service_key,weight,pickup_day,pickup_slot,"
                     "address_text,service_cost,delivery_fee,total,payment_method,stage,cancelled,created_at,"
                     "picked_at,eta,ready_by,partner) VALUES(?,1,1,'laundry',?,'Today','Morning (8–11 AM)',?,?,0,?,"
                     "'UPI',4,0,?,?,?,?,'Ravi')",
                     (f"LP-{n}", w, addr, cost, cost, f(created), f(created + dt.timedelta(hours=1)),
                      f(created + dt.timedelta(days=1, hours=1)), f(created + dt.timedelta(hours=6))))
        n += 1
    
    c = today - dt.timedelta(days=1) + dt.timedelta(hours=17)
    conn.execute("INSERT INTO orders(code,user_id,provider_id,service_key,weight,pickup_day,pickup_slot,address_text,"
                 "service_cost,delivery_fee,total,payment_method,stage,cancelled,created_at,picked_at,eta,ready_by,"
                 "partner) VALUES('LP-20479',1,3,'laundry',4,'Today','Evening (4–7 PM)',?,276,0,276,'Card',2,0,?,?,?,?,'Imran')",
                 (addr, f(c), f(c + dt.timedelta(hours=1)), f(today + dt.timedelta(hours=11)),
                  f(today - dt.timedelta(days=1) + dt.timedelta(hours=16))))
    
    c = today + dt.timedelta(hours=8, minutes=30)
    conn.execute("INSERT INTO orders(code,user_id,provider_id,service_key,weight,pickup_day,pickup_slot,address_text,"
                 "service_cost,delivery_fee,total,payment_method,stage,cancelled,created_at,picked_at,eta,ready_by,"
                 "partner) VALUES('LP-20480',1,2,'ironing',5,'Tomorrow','Morning (8–11 AM)',?,312,0,312,'Wallet',0,0,?,NULL,?,?,'Suresh')",
                 (addr, f(c), f(today + dt.timedelta(days=2, hours=11)), f(today + dt.timedelta(days=1, hours=16))))
    
    c = today + dt.timedelta(hours=9, minutes=40)
    conn.execute("INSERT INTO orders(code,user_id,provider_id,service_key,weight,pickup_day,pickup_slot,address_text,"
                 "service_cost,delivery_fee,total,payment_method,stage,cancelled,created_at,picked_at,eta,ready_by,"
                 "partner) VALUES('LP-20481',1,1,'laundry',3,'Today','Morning (8–11 AM)',?,237,0,237,'UPI',1,0,?,?,?,?,'Ravi')",
                 (addr, f(c), f(today + dt.timedelta(hours=10, minutes=20)),
                  f(today + dt.timedelta(days=1, hours=11)), f(today + dt.timedelta(hours=16))))
    phones = {"Ravi": "9876500001", "Imran": "9876500002", "Suresh": "9876500003", "Kiran": "9876500004"}
    for name, phone in phones.items():
        conn.execute("UPDATE orders SET partner_phone=? WHERE partner=?", (phone, name))
    
    comments = ["Clothes came back fresh and folded neatly.", "On time pickup and delivery.", "Great value for the price.",
                "Very careful with my shirts.", "Friendly delivery partner.", "Smells great, no stains left."]
    for i, r in enumerate([5, 5, 5, 5, 5, 5, 5, 5, 5, 4]):
        conn.execute("INSERT INTO reviews(order_id,user_id,provider_id,reviewer_name,rating,comment,created_at) "
                     "VALUES(?,1,1,'Rahul Sharma',?,?,?)", (i + 1, r, comments[i % 6], f(today - dt.timedelta(days=28 - i * 2))))
    for pid, ratings in ((2, [5, 5, 5, 5, 4, 5, 5, 5, 5, 4]), (3, [5, 5, 4, 5, 4, 5, 5, 4, 5, 5])):
        for i, r in enumerate(ratings):
            conn.execute("INSERT INTO reviews(provider_id,reviewer_name,rating,comment,created_at) VALUES(?,?,?,?,?)",
                         (pid, ["Ananya K.", "Meera S.", "Vikram P.", "Sana R.", "Arjun D."][i % 5], r, comments[(i + pid) % 6],
                          f(today - dt.timedelta(days=40 - i * 3))))
    conn.commit()



def _all(sql, args=()):
    return [dict(r) for r in conn.execute(sql, args).fetchall()]


def _one(sql, args=()):
    r = conn.execute(sql, args).fetchone()
    return dict(r) if r else None


def authenticate(identifier, password):
    ident = identifier.strip().lower()
    digits = "".join(ch for ch in ident if ch.isdigit())[-10:]
    user = _one("SELECT * FROM users WHERE lower(email)=? OR (? != '' AND phone=?)", (ident, digits, digits))
    if user and secrets.compare_digest(_hash(password, user["salt"]), user["pw_hash"]):
        return user
    return None


def create_user(name, email, phone, password):
    if _one("SELECT id FROM users WHERE lower(email)=?", (email.lower(),)):
        raise ValueError("An account with this email already exists.")
    salt = secrets.token_hex(8)
    cur = conn.execute("INSERT INTO users(name,email,phone,pw_hash,salt,photo) VALUES(?,?,?,?,?,NULL)",
                       (name, email.lower(), phone, _hash(password, salt), salt))
    conn.commit()
    return get_user(cur.lastrowid)


def get_user(uid):
    return _one("SELECT * FROM users WHERE id=?", (uid,))


def update_user(uid, name, email, phone):
    other = _one("SELECT id FROM users WHERE lower(email)=? AND id!=?", (email.lower(), uid))
    if other:
        raise ValueError("That email is already used by another account.")
    conn.execute("UPDATE users SET name=?, email=?, phone=? WHERE id=?", (name, email.lower(), phone, uid))
    conn.commit()
    return get_user(uid)


def addresses(uid):
    return _all("SELECT * FROM addresses WHERE user_id=? ORDER BY is_default DESC, id", (uid,))


def default_address(uid):
    rows = addresses(uid)
    return rows[0] if rows else None


def add_address(uid, label, street, area, city, pincode, make_default=False):
    first = not addresses(uid)
    if make_default or first:
        conn.execute("UPDATE addresses SET is_default=0 WHERE user_id=?", (uid,))
    cur = conn.execute("INSERT INTO addresses(user_id,label,street,area,city,pincode,is_default) VALUES(?,?,?,?,?,?,?)",
                       (uid, label, street, area, city, pincode, 1 if (make_default or first) else 0))
    conn.commit()
    return cur.lastrowid


def set_default_address(uid, aid):
    conn.execute("UPDATE addresses SET is_default=0 WHERE user_id=?", (uid,))
    conn.execute("UPDATE addresses SET is_default=1 WHERE id=? AND user_id=?", (aid, uid))
    conn.commit()


def delete_address(uid, aid):
    was_default = _one("SELECT is_default FROM addresses WHERE id=? AND user_id=?", (aid, uid))
    conn.execute("DELETE FROM addresses WHERE id=? AND user_id=?", (aid, uid))
    if was_default and was_default["is_default"]:
        left = addresses(uid)
        if left:
            conn.execute("UPDATE addresses SET is_default=1 WHERE id=?", (left[0]["id"],))
    conn.commit()


def services():
    return _all("SELECT * FROM services ORDER BY sort_order")


def service(key):
    return _one("SELECT * FROM services WHERE key=?", (key,))


def _with_rating(p):
    """Provider rating is the average of its reviews (falls back to the stored value if none)."""
    if p:
        r = _one("SELECT COUNT(*) AS c, AVG(rating) AS a FROM reviews WHERE provider_id=?", (p["id"],))
        p["review_count"] = r["c"]
        if r["c"]:
            p["rating"] = round(r["a"], 1)
    return p


def providers():
    return [_with_rating(p) for p in _all("SELECT * FROM providers ORDER BY id")]


def provider(pid):
    return _with_rating(_one("SELECT * FROM providers WHERE id=?", (pid,)))


# ------------------------------------------------------------------ reviews
def provider_reviews(pid, limit=20):
    return _all("SELECT id, reviewer_name, rating, comment, created_at FROM reviews "
                "WHERE provider_id=? ORDER BY id DESC LIMIT ?", (pid, limit))


def review_for_order(oid):
    return _one("SELECT * FROM reviews WHERE order_id=?", (oid,))


def add_review(order, user, rating, comment):
    cur = conn.execute("INSERT INTO reviews(order_id,user_id,provider_id,reviewer_name,rating,comment,created_at) "
                       "VALUES(?,?,?,?,?,?,?)", (order["id"], user["id"], order["provider_id"], user["name"], rating,
                                                 comment, dt.datetime.now().strftime(FMT)))
    conn.commit()
    return cur.lastrowid

def next_order_code():
    row = _one("SELECT MAX(CAST(substr(code,4) AS INTEGER)) AS m FROM orders")
    return f"LP-{(row['m'] or 20000) + 1}"


def insert_order(**v):
    cols = ",".join(v)
    marks = ",".join("?" for _ in v)
    cur = conn.execute(f"INSERT INTO orders({cols}) VALUES({marks})", tuple(v.values()))
    conn.commit()
    return cur.lastrowid


def orders(uid):
    return _all("SELECT * FROM orders WHERE user_id=? ORDER BY id DESC", (uid,))


def order(oid):
    return _one("SELECT * FROM orders WHERE id=?", (oid,))


def latest_order(uid):
    return _one("SELECT * FROM orders WHERE user_id=? ORDER BY id DESC LIMIT 1", (uid,))


def update_order(oid, **v):
    sets = ",".join(f"{k}=?" for k in v)
    conn.execute(f"UPDATE orders SET {sets} WHERE id=?", (*v.values(), oid))
    conn.commit()


def counters(uid):
    """Numbers for the 'My Orders' card on the Account screen."""
    r = _one("""SELECT
        SUM(cancelled=0 AND stage=0) AS current,
        SUM(cancelled=0 AND stage BETWEEN 1 AND 3) AS picked,
        SUM(cancelled=0 AND stage=4) AS delivered,
        SUM(cancelled=1) AS cancelled FROM orders WHERE user_id=?""", (uid,))
    return [int(r[k] or 0) for k in ("current", "picked", "delivered", "cancelled")]