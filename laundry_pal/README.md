# Laundry Pal — Python (Tkinter) desktop app

A phone-shaped laundry-booking app: Login → Home → Providers → Provider Details → Review & Payment → Order Tracking → Account.
Built **only** with Python 3, Tkinter (Canvas + Entry), Pillow and SQLite (`sqlite3`). No HTML/CSS/JS, no web frameworks.

## Install & run
```bash
pip install -r requirements.txt        # just Pillow
python main.py
```
Tkinter ships with the python.org installers for Windows/macOS. On Debian/Ubuntu: `sudo apt install python3-tk`.
The database `laundry_pal.db` is created and seeded automatically on first run (delete it to reset the demo data).

## Demo login
| Email | Password |
|---|---|
| `aarav.sharma@email.com` (or phone `9876543210`) | `demo123` |

You can also create your own account with **Sign up**.

## Test the full booking journey
1. Log in with the demo account.
2. Home → tap **Laundry** (or search "blue" and press Enter).
3. Providers → try **Filter** and **Sort**, then tap **FreshFold Laundry**.
4. Provider Details → **Book Now**.
5. Review & Payment → tap the **Details** row to change weight/day/slot, tap **Change** to pick another address, choose a payment method, press **Place Order**. A *simulated* payment runs.
6. Order Tracking → press **Simulate next stage ›** to move Picked up → Washing → Ironing → Out for delivery → Delivered (a brand-new order can also be cancelled before pickup).
7. Profile tab → counters update; try **Edit**, **Manage** (add / delete / set default address) and **Sign Out**.
8. Orders tab → full history; tap any order to open its tracking page.

Automated check: `python tests/test_journey.py` (drives the real screens; on a headless Linux box prefix with `xvfb-run`).
`python tests/screenshots.py` saves a PNG of every screen to `screenshots/` for comparison with `reference/`.

## Pricing rules
`service cost = round(price per kg × service multiplier) × kg` (Laundry ×1.0, Ironing ×0.7, Dry Clean ×2.2).
Delivery is free if the provider offers free delivery or the cost reaches its "free above" amount, otherwise a flat fee.
Orders below the provider's minimum order (e.g. ₹199 for FreshFold) are rejected with a message. Weight must be 1–25 kg.

## Project layout
```
main.py            entry point
app.py             window, session state, navigation stack
config.py          design system: colours, fonts, 430x932 size, scaling
database.py        SQLite schema, seed data, queries
screens/           login (+signup), home, providers, provider_details, checkout, tracking, profile, orders
components/        surface.py (canvas drawing helpers + inputs), icons.py, images.py, navigation.py, sheets.py
services/          pricing_service.py, booking_service.py, validation.py
assets/images/     photos (cropped from the Figma frames — replace with your own, same file names)
reference/         the 7 Figma screenshots;  make_assets.py re-creates the crops
```

## Honest notes
* Payment and tracking are **simulations** — no real money or GPS.
* Photos are cropped from the Figma frames, so they are low-resolution; swap in higher-quality licensed images in `assets/images/` (same names).
* Provider images for Sparkle / Blue Basket reuse their list photos on the details page.
* Only 3 providers are seeded (the design says "12"); the count shown is the real number after filters.
* The window scales itself down automatically on screens shorter than ~1040 px.
* Added beyond the mock-ups (needed for working features): Sign-up screen, Orders tab, bottom sheets (filter, sort, weight & pickup, addresses, edit profile), "Change" link and chevron on the checkout card, and a Simulate/Cancel control on the tracking screen.
* Font: uses Inter if installed, otherwise Segoe UI / Helvetica / Arial / DejaVu Sans, so text widths differ slightly from Figma.
