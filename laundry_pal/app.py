"""Main application window: owns the database connection, the session state and
the navigation stack.  Screens are Frames that are swapped inside one window."""
import tkinter as tk
from types import SimpleNamespace

import config
import database as db
from config import C
from screens.checkout import CheckoutScreen
from screens.home import HomeScreen
from screens.login import LoginScreen, SignupScreen
from screens.orders import OrdersScreen
from screens.profile import ProfileScreen
from screens.provider_details import ProviderDetailsScreen
from screens.providers import ProvidersScreen
from screens.tracking import TrackingScreen

SCREENS = {
    "login": LoginScreen, "signup": SignupScreen, "home": HomeScreen, "providers": ProvidersScreen,
    "details": ProviderDetailsScreen, "checkout": CheckoutScreen, "tracking": TrackingScreen,
    "profile": ProfileScreen, "orders": OrdersScreen,
}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Laundry Pal")
        self.configure(bg=C.BG)
        self.resizable(False, False)
        config.resolve_font_family(self)
        # shrink the phone on small screens so it always fits
        config.set_scale(round(max(0.6, min(1.0, (self.winfo_screenheight() - 110) / config.H)), 2))
        db.connect(config.DB_PATH)

        self.container = tk.Frame(self, bg=C.BG)
        self.container.pack()
        self.history, self.current, self.screen = [], None, None
        self.reset_session()
        self.geometry(f"+{max(0, (self.winfo_screenwidth() - config.sc(config.W)) // 2)}+10")
        self.go("login", reset=True)

    # ------------------------------------------------------------ session
    def reset_session(self):
        self.session = SimpleNamespace(
            user=None, service_key="laundry", provider_id=None, query="", order_id=None,
            filters={"rating": None, "price": None, "pickup": None}, sort="rating",
            booking={"weight": 3, "day": "Today", "slot": None, "address_id": None, "payment": "upi"})

    def service(self):
        return db.service(self.session.service_key)

    def provider(self):
        return db.provider(self.session.provider_id)

    # ------------------------------------------------------------ navigation
    def _show(self, name, params):
        if self.screen is not None:
            self.screen.destroy()
        self.screen = SCREENS[name](self, **params)
        self.screen.pack()
        self.current = (name, params)

    def go(self, name, reset=False, **params):
        """Open a screen.  The previous screen is pushed on the history stack so Back works."""
        if reset:
            self.history = []
        elif self.current:
            self.history.append(self.current)
        self._show(name, params)

    def back(self):
        if self.history:
            name, params = self.history.pop()
            self._show(name, params)
        else:
            self.go("home", reset=True)

    def tab(self, name):
        """Bottom navigation: jump to a top-level tab."""
        self.history = []
        self._show(name, {})

    def go_with_history(self, stack, name, **params):
        self.history = list(stack)
        self._show(name, params)

    def logout(self):
        self.reset_session()
        self.go("login", reset=True)
