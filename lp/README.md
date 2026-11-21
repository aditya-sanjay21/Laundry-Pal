# Laundry Pal (React Native + Flask)

Capstone project, Group 6. The customer app is **React Native (Expo)**; the backend is a **Flask REST API with SQLite**.

## 1. Run the backend (your computer)
```
cd backend
pip install -r requirements.txt
python app.py            # serves http://0.0.0.0:5000
```
Delete `backend/laundry_pal.db` first if you ran an older version, so the database is recreated with the new tables.
Demo login: `rahul.sharma@email.com` / `demo123`. Check it works: open `http://localhost:5000/api/services`.

## 2. Run the app (Expo Go on your phone)

Phone and computer must be on the same Wi-Fi. Install **Expo Go** from the Play Store / App Store.
```
cd mobile
npm install
npx expo start
```

Scan the QR code with Expo Go. The app finds the backend from the QR address automatically. If it cannot connect, set MANUAL_URL in mobile/src/config.js (e.g. http://192.168.1.5:5000) and allow port 5000 in your firewall. On an Android emulator it uses 10.0.2.2:5000.

## 3. Tests
`python tests/api_test.py` checks the new endpoints (payment retry, reschedule, review rules).

## Faculty feedback (Milestone 1) -> what is in the app
| Feedback | In the app |
|---|---|
| Missing: Schedule pickup screen | `Schedule.js`: weight, day, time slot, address |
| Missing: Service selection | Home service cards + service chips on Provider Details |
| Missing: Orders list | `Orders.js` (Active / Past tabs) |
| Missing: Login digital screen, sign-up story | `Auth.js` (Login and Sign Up) |
| Missing: cancel or reschedule | Tracking: Cancel order, Reschedule pickup (only before pickup) |
| Missing: rate and review | `Review.js`; provider rating is the average of reviews |
| Missing: contact pickup partner | Tracking: Call button |
| Missing: failed payment | Checkout saves the order, then Retry; unpaid orders can be paid from Tracking |
| Navigation flow | Bottom tabs (Home, Orders, Profile) + stack; returning user: Home or Orders -> Tracking |
| Persona consistency | Demo user is now Rahul Sharma |
| Provider and partner roles | Out of scope; `POST /orders/:id/advance` simulates status updates ("Demo" button) |

## API (all under /api)
Auth: `POST /auth/signup`, `POST /auth/login` · Profile: `GET/PUT /me` · Addresses: `GET/POST /addresses`, `PUT /addresses/:id/default`, `DELETE /addresses/:id`
Catalogue: `GET /services`, `GET /providers`, `GET /providers/:id`, `GET /providers/:id/reviews`, `POST /quote`
Orders: `POST /orders`, `GET /orders`, `GET /orders/:id`, `GET /orders/latest`, `PUT /orders/:id` (reschedule), `POST /orders/:id/cancel`,
`POST /orders/:id/payment`, `POST /orders/:id/review`, `POST /orders/:id/advance` (simulation)
