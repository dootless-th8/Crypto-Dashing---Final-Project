import tkinter as tk
from tkinter import ttk
import websocket
import json
import threading
import requests


# Essentails libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class CryptoTicker:
    """Reusable ticker component for any cryptocurrency."""
    
    def __init__(self, parent, symbol, display_name):
        self.parent = parent
        self.symbol = symbol.lower()
        self.display_name = display_name
        self.is_active = False
        self.ws = None

        self._latest_price = None
        self._latest_change = None
        self._latest_percent = None

        self._ui_job = None
        self._ui_interval = 300  # ms
        self._generation = 0

        # Setup Color for each frames        
        style = ttk.Style()
        style.configure('TFrame', background='gray11')       # Setting the bg
        style.configure('Fra1.TFrame',background='gray30')        # Setting the elements bg
        style.configure('Fra2.TFrame',background='CadetBlue4')        # Setting the elements bg

        # Creat bg panel
        self.frame = ttk.Frame(parent, relief="solid", borderwidth=1, padding=20, style='Fra1.TFrame')    

        # Title
        ttk.Label(self.frame, text=display_name, font=("Arial", 16, "bold"), background='gray19').pack()
        
        # Price
        self.price_label = tk.Label(self.frame, text="--,---", font=("Arial", 16, "bold"), background='gray19')
        # self.price_label.configure(bg='azure')
        self.price_label.pack(pady=10)
        
        # Change
        self.change_label = ttk.Label(self.frame, text="--", font=("Arial", 12), background='gray19')
        self.change_label.pack()
    
    def start(self):
        """Start WebSocket connection."""
        if self.is_active:
            return
        
        self.is_active = True
        self._generation += 1
        gen = self._generation

        ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol}@ticker"
        
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self.on_message,
            on_error=lambda ws, err: print(f"{self.symbol} error: {err}"),
            on_close=lambda ws, s, m: print(f"{self.symbol} closed"),
            on_open=lambda ws: print(f"{self.symbol} connected")
        )
        
        threading.Thread(target=self.ws.run_forever, daemon=True).start()
        self._ui_loop(gen)
    
    def stop(self):
        """Stop WebSocket connection."""
        self.is_active = False
        self._generation += 1

        if self._ui_job:
            self.parent.after_cancel(self._ui_job)
            self._ui_job = None

        if self.ws:
            self.ws.close()
            self.ws = None
    
    def on_message(self, ws, message):
        """Handle price updates."""
        if not self.is_active:
            return
        
        try:
            data = json.loads(message)
            self._latest_price = float(data['c'])
            self._latest_change = float(data['p'])
            self._latest_percent = float(data['P'])
        except Exception:
            return
    

    def _ui_loop(self, gen):
        if not self.is_active or gen != self._generation:
            return

        if self._latest_price is not None:
            price = self._latest_price
            change = self._latest_change
            percent = self._latest_percent

            color = "green" if change >= 0 else "red"
            sign = "+" if change >= 0 else ""

            self.price_label.config(text=f"{price:,.2f}", fg=color)
            self.change_label.config(
                text=f"{sign}{change:,.2f} ({sign}{percent:.2f}%)",
                foreground=color
            )

        self._ui_job = self.parent.after(
            self._ui_interval,
            lambda: self._ui_loop(gen)
        )


    def set_symbol(self, symbol, display_name):
        self.stop()
        self.symbol = symbol.lower()
        self.display_name = display_name
        self.frame.winfo_children()[0].config(text=display_name)
        self.start()
        
    def update_display(self, price, change, percent):
        """Update the ticker display."""
        if not self.is_active:
            return
        
        color = "green" if change >= 0 else "red"
        self.price_label.config(text=f"{price:,.2f}", fg=color)
        
        sign = "+" if change >= 0 else ""
        self.change_label.config(
            text=f"{sign}{change:,.2f} ({sign}{percent:.2f}%)",
            foreground=color
        )
    
    def pack(self, **kwargs):
        """Allow easy placement of ticker."""
        self.frame.pack(**kwargs)
    
    def pack_forget(self):
        """Hide the ticker."""
        self.frame.pack_forget()

    # def grid_forget(self):
    #     self.frame.grid_forget()