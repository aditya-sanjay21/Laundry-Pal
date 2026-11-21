"""Base class for every screen: a Frame holding one Surface (canvas)."""
import tkinter as tk

from components import navigation
from components.surface import Surface
from config import C


class Screen(tk.Frame):
    nav_tab = None          # 'home' / 'orders' / 'profile' -> shows the bottom nav bar

    def __init__(self, app, **params):
        super().__init__(app.container, bg=C.BG)
        self.app, self.params = app, params
        self.c = Surface(self)
        self.c.pack()
        self.c.status_bar()
        self.build()
        if self.nav_tab:
            navigation.draw(self.c, self.nav_tab, self.app.tab)
        self.c.home_indicator()
        self.c.frame_border()

    def build(self):
        raise NotImplementedError

    def redraw(self):
        """Rebuild the whole screen (used after data changes)."""
        self.c.destroy_widgets()
        self.c.delete("all")
        self.c._imgs.clear()
        self.c.status_bar()
        self.build()
        if self.nav_tab:
            navigation.draw(self.c, self.nav_tab, self.app.tab)
        self.c.home_indicator()
        self.c.frame_border()

    def destroy(self):
        self.c.destroy_widgets()
        super().destroy()
