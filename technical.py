# technical.py
import tkinter as tk
from tkinter import ttk
import threading
import requests
from datetime import datetime
import time
import numpy as np
import matplotlib.patches as patches
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Pain
DARK_BG = "#1e1e1e"
PANEL_BG = "#262626"
GRID = "#444444"
WHITE = "#e0e0e0"
GREEN = "#4caf50"
RED = "#f44336"
GRAY = "#b0b0b0"

FONT_SMALL = 8
FONT_TITLE = 10


class TechnicalAnalysisPanel:
    def __init__(self, parent, symbol, interval_seconds=3):
        self.parent = parent
        self.symbol = symbol.upper()
        self.interval_seconds = interval_seconds


        # State configs
        self._stop_event = threading.Event()
        self._thread = None
        self._klines = []



        # Graph set-up
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.fig = Figure(figsize=(6, 5), dpi=100, facecolor=DARK_BG)
        self.ax_price = self.fig.add_subplot(211)
        self.ax_vol = self.fig.add_subplot(212, sharex=self.ax_price)
        self._style_axes()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        
        self.start()

    # graph aesthetic
    def _style_axes(self):
        for ax in (self.ax_price, self.ax_vol):
            ax.set_facecolor(PANEL_BG)
            ax.grid(True, color=GRID, linestyle="--", linewidth=0.4)
            ax.tick_params(colors=GRAY)

        self.ax_price.set_ylabel("Price", color=GRAY, fontsize=FONT_SMALL)
        self.ax_vol.set_ylabel("Volume", color=GRAY, fontsize=FONT_SMALL)

    
    # fetch me thy soul
    def fetch_klines(self):
        try:
            url = "https://api.binance.com/api/v3/klines"
            params = {"symbol": self.symbol, "interval": "1h", "limit": 50}
            r = requests.get(url, params=params, timeout=5)
            data = r.json()
            return data if isinstance(data, list) else []
        except Exception:
            return []

    
    # The torture
    def plot(self, klines):
        if not klines:
            return

        self.ax_price.clear()
        self.ax_vol.clear()
        self._style_axes()

        times = [datetime.fromtimestamp(k[0] / 1000) for k in klines]
        ohlc = np.array([[float(x) for x in k[1:5]] for k in klines])
        volumes = np.array([float(k[5]) for k in klines])
        width = 0.6


        # Bloody Palace
        for i, (o, h, l, c) in enumerate(ohlc):
            color = GREEN if c >= o else RED
            self.ax_price.plot([i, i], [l, h], color=color, linewidth=1)
            self.ax_price.add_patch(
                patches.Rectangle(
                    (i - width / 2, min(o, c)),
                    width,
                    max(abs(c - o), 0.0001),
                    facecolor=color,
                    edgecolor=color,
                )
            )

        for i, v in enumerate(volumes):
            color = GREEN if ohlc[i][3] >= ohlc[i][0] else RED
            self.ax_vol.bar(i, v, color=color, width=width)

        ticks = range(0, len(times), max(1, len(times) // 6))
        labels = [times[i].strftime("%m-%d %H:%M") for i in ticks]

        self.ax_vol.set_xticks(list(ticks))
        self.ax_vol.set_xticklabels(labels, fontsize=FONT_SMALL, color=GRAY)
        self.ax_price.tick_params(labelbottom=False)

        self.ax_price.set_title(
            f"{self.symbol} 1 Hour Candlestick (Last 50)",
            color=WHITE,
            fontsize=FONT_TITLE,
        )

        self.fig.tight_layout()
        self.canvas.draw_idle()

    

    def _run_loop(self):
        while not self._stop_event.is_set():
            klines = self.fetch_klines()
            if klines:
                self.parent.after(0, self.plot, klines)
            time.sleep(self.interval_seconds)



    def start(self):
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run_loop, daemon=True
        )
        self._thread.start()


    def stop(self):
        self._stop_event.set()

    def set_symbol(self, symbol):
        self.symbol = symbol.upper()




    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def pack_forget(self):
        self.frame.pack_forget()
