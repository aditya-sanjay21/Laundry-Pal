# Laundry Pal — viva cheat-sheet

**What is it?** A desktop GUI app in Python that imitates a mobile laundry-booking app. Tkinter draws the UI, SQLite stores the data, Pillow handles photos.

**Architecture (layers)**
1. *UI layer* — `screens/` (one class per screen) built from `components/` (reusable drawing helpers).
2. *Logic layer* — `services/` (pricing, booking, validation) has no Tkinter code, so it can be tested alone.
3. *Data layer* — `database.py` is the only file that writes SQL.
4. `app.py` glues them: it owns the window, the logged-in user ("session") and the screen history stack.

**How screens work.** Every screen is a `tk.Frame` that holds one `Surface`, a subclass of `tk.Canvas`. Rounded cards, text, icons and buttons are canvas items; clicking is done with `tag_bind`. Text boxes are real `tk.Entry` widgets embedded with `create_window`. Navigation = destroy the old Frame, create the new one inside the same window (`App.go`, `App.back`, `App.tab`).

**Key ideas to mention**
* *Logical coordinates + `sc()`* — all positions use the 430×932 Figma size; `sc()` multiplies by a scale factor so the app fits small screens.
* *Rounded rectangles* — a polygon with `smooth=True` (Tk has no rounded-rect primitive). Photos get rounded corners with a Pillow mask.
* *Icons* — drawn from lines/arcs/ovals on a 24×24 grid (`components/icons.py`); no emoji, no image files.
* *Radio buttons* — a `tk.StringVar` holds the payment method; a trace callback repaints the canvas circles (selection control, custom look).
* *Placeholder text* — `PlaceholderEntry` subclasses `tk.Entry` (Tk has none built in).
* *Bottom sheets* — a semi-transparent Pillow image dims the screen, then a rounded white panel is drawn with the tag `"ov"`; closing = `delete("ov")` and destroying its entries.
* *Passwords* — stored as salted PBKDF2-SHA256 hashes, never as plain text.
* *SQL safety* — all queries use `?` placeholders (prevents SQL injection).
* *Order stages* — an integer `stage` 0–4 in the `orders` table drives the timeline; "Simulate" just increments it, so progress survives restarts.
* *Pricing* — one function `quote()` is used by checkout, order creation and tests, so numbers never disagree.

**Database tables.** `users`, `addresses` (many per user, one default), `services`, `providers`, `orders` (links user, provider, service; stores totals, payment method, stage).

**Limitations to be upfront about.** Simulated payment, no live tracking, only 3 seeded providers, photos are low-res crops from the mock-ups, canvas lines are not anti-aliased so icons look slightly crisper/heavier than Figma.

**Likely questions**
* *Why Canvas instead of ttk widgets?* ttk can't reproduce rounded cards, custom icons or the timeline.
* *Why not one big file?* Separation of concerns: easier to test and explain.
* *How would you add a real payment gateway?* Replace the animation in `CheckoutScreen.show_payment_overlay/finish_payment` with a call to the gateway's API and only create the order on success.
