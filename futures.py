import tkinter as tk
from tkinter import ttk
import threading
import requests
import time


class BuySellRatioPanel:    

    def __init__(self, parent, symbol, interval="5m", title="5 Minute Volume & Ratio"):
        self.parent = parent
        self.symbol = symbol.upper()
        self.interval = interval
        self.running = False

        self._thread = None
        self._update_seconds = 5

        # Main frame
        self.frame = ttk.Frame(
            self.parent, relief="solid", borderwidth=1, padding=10, style="Fra1.TFrame"
        )

        # Title
        self.title_lbl = tk.Label(
            self.frame, text=title, font=("Arial", 10, "bold"),
            fg="white", bg="gray19", anchor="w"
        )
        self.title_lbl.pack(fill=tk.X, pady=(0, 5))



        # Buy / Sell row 
        mid_frm = ttk.Frame(self.frame, style="Fra1.TFrame")
        mid_frm.pack(fill=tk.X)

        self.buy_lbl = tk.Label(
            mid_frm, text="Buy: 0.00", fg="#57b045",
            bg="gray19", font=("Arial", 15, "bold")
        )
        self.buy_lbl.pack(side=tk.LEFT)

        self.sell_lbl = tk.Label(
            mid_frm, text="Sell: 0.00", fg="#ff4444",
            bg="gray19", font=("Arial", 15, "bold")
        )
        self.sell_lbl.pack(side=tk.LEFT)


        # Ratio labl
        self.ratio_lbl = tk.Label(
            self.frame, text="Ratio: 0.000", fg="#6fa8dc",
            bg="gray19", font=("Arial", 15, "bold")
        )
        self.ratio_lbl.pack(anchor="w")    


        
    def start(self):
        if self.running:
            return
        self.running = True

        self._thread = threading.Thread(
            target=self._run_loop, daemon=True
        )
        self._thread.start()

    def stop(self):
        self.running = False

    def set_symbol(self, symbol):
        self.stop()
        self.symbol = symbol.upper()

        base = self.title_lbl.cget("text").split("(")[0]
        self.title_lbl.config(text=f"{base}({self.symbol})")

        self.start()


    
    # Data
    def fetch_trades(self):
        url = "https://api.binance.com/api/v3/klines"
        params = {
            "symbol": self.symbol,
            "interval": self.interval,
            "limit": 1
        }
        try:
            resp = requests.get(url, params=params, timeout=5)
            data = resp.json()
            return data if isinstance(data, list) else []
        except Exception:
            return []


    # Loop thingy
    def _run_loop(self):
        while self.running:
            klines = self.fetch_trades()
            if klines:
                k = klines[0]
                buy_vol = float(k[9])
                total_vol = float(k[5])
                sell_vol = total_vol - buy_vol
                ratio = buy_vol / total_vol if total_vol > 0 else 0

                self.parent.after(
                    0,
                    self._update_labels,
                    buy_vol, sell_vol, ratio
                )

            time.sleep(self._update_seconds)


    def _update_labels(self, buy_vol, sell_vol, ratio):
        if not self.running:
            return

        self.buy_lbl.config(text=f"Buy: {buy_vol:,.2f}")
        self.sell_lbl.config(text=f"Sell: {sell_vol:,.2f}")
        self.ratio_lbl.config(text=f"Ratio: {ratio:,.3f}")

  
    
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def pack_forget(self):
        self.frame.pack_forget()
