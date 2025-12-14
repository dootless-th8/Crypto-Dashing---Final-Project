import tkinter as tk
from tkinter import ttk
import websocket
import json
import threading
import requests


# Import Classes
import ticker
import order_book
import technical
import futures


TOKENS = {
    "BTC": "btcusdt",
    "ETH": "ethusdt",
    "SOL": "solusdt",
    "BNB": "bnbusdt",
    "ADA": "adausdt",
    "XRP": "xrpusdt",
}


class ToggleableTickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Dashboard")
        self.root.minsize(1400, 730)
        self.root.geometry("1400x1000")
        self.current_sym = "btcusdt"
        self.token_buttons = {}


        # Control panel
        control_frm = ttk.Frame(self.root, padding=10)
        control_frm.pack(fill=tk.X)
        
        tk.Label(control_frm, text='Crypto_Dash'.upper(), anchor='ne', font=("Arial", 18),foreground='dark khaki', background='gray11').pack(side=tk.RIGHT)

        self.tick_btn = ttk.Button(
            control_frm, 
            text=f"Show {self.current_sym.upper()}/USDT",
            command=self.toggle_tick
        )
        self.tick_btn.pack(side=tk.LEFT, padx=4, pady=5)


        for name, sym in TOKENS.items():
            btn = ttk.Button(
                control_frm,
                text=name,
                command=lambda s=sym, n=name: self.switch_symbol(s, n)
            )
            btn.pack(side=tk.LEFT, padx=4, pady=5)
            self.token_buttons[name] = btn
        
        # Highlight initially
        self.token_buttons["BTC"].state(["pressed"])
        
        
        # Main gist
        content = ttk.Frame(self.root)
        content.pack(fill=tk.BOTH, expand=True)


        content.grid_columnconfigure(0, weight=2)  # BTC price
        content.grid_columnconfigure(1, weight=4)  # Best Bid/Ask
        content.grid_columnconfigure(2, weight=2)  # 5 min ratio
        content.grid_columnconfigure(3, weight=2)  # 1 hour ratio
        content.grid_rowconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)


        

        # !!!! Create tickers !!!!
        self.btc_ticker = ticker.CryptoTicker(content, "btcusdt", "BTC/USDT")
        self.btc_ticker.frame.grid(row=0, column=0, sticky='new', padx=10)
        # self.btc_ticker.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
                               
        # 5-minute ratio card
        self.ratio_panel_5m = futures.BuySellRatioPanel(content, self.current_sym, title="5 Minute Volume & Ratio")
        self.ratio_panel_5m.frame.grid(row=0, column=2, sticky="new", padx=10)

        # 1-hour ratio card
        self.ratio_panel_1h = futures.BuySellRatioPanel(content, self.current_sym, title="1 Hour Volume & Ratio")
        self.ratio_panel_1h.frame.grid(row=0, column=3, sticky="new", padx=10)
        

        # self.eth_ticker = ticker.CryptoTicker(content, "ethusdt", "ETH/USDT")
        # self.eth_ticker.frame.grid(row=0, column=4, sticky='new')
        # self.eth_ticker.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        # self.sol_ticker = ticker.CryptoTicker(self.root, "solusdt", "SOL/USDT")
        # Don't pack SOL initially (hidden)


         # !!!! Top order books !!!!        
        order_sec_frm = ttk.Frame(content, padding=10, style='TFrame')
        order_sec_frm.grid(row=1, column=0, columnspan=2, sticky='nsw')
        # order_sec_frm.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        grid_frame = ttk.Frame(order_sec_frm, padding=6, style='Fra1.TFrame')
        grid_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.Order = order_book.OrderBookPanel(grid_frame, "btcusdt", content)
        self.Order.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)                


        technical_frm = ttk.Frame(content, padding=10, style='Fra1.TFrame')
        technical_frm.grid(row=1, column=2, columnspan=3, sticky='nsw')

        self.technic = technical.TechnicalAnalysisPanel(technical_frm, self.current_sym)
        self.technic.pack(fill=tk.BOTH, expand=True)
        # self.Order.frame.grid(row=0, column=0, sticky='N')

        
        self.start_all()
        
        self.tick_visible = True
        

    
    def switch_symbol(self, symbol, name):
        if symbol == self.current_sym:
            return

        self.current_sym = symbol

        self.tick_btn.configure(text=f"Show {self.current_sym.upper()}/USDT")
        self.btc_ticker.set_symbol(symbol, f"{name}/USDT")
        self.Order.set_symbol(symbol)
        self.technic.set_symbol(symbol)
        self.ratio_panel_5m.set_symbol(symbol)
        self.ratio_panel_1h.set_symbol(symbol)

        for k, btn in self.token_buttons.items():
            btn.state(["!pressed"])
            if k == name:
                btn.state(["pressed"])
        

    def start_all(self):
        self.btc_ticker.start()
        self.Order.start()
        self.technic.start()
        self.ratio_panel_5m.start()
        self.ratio_panel_1h.start()
    
    def toggle_tick(self):
        """Show or hide SOL ticker."""
        if self.tick_visible:
            # Hide SOL
            self.btc_ticker.stop()
            self.btc_ticker.frame.grid_forget()
            self.tick_btn.config(text=f"Show {self.current_sym.upper()}/USDT")
            self.tick_visible = False
        else:
            # Show SOL
            self.btc_ticker.frame.grid(row=0, column=0, sticky='new', padx=10)
            self.btc_ticker.start()
            self.tick_btn.config(text=f"Hide {self.current_sym.upper()}/USDT")
            self.tick_visible = True
    
    def on_closing(self):
        self.btc_ticker.stop()
        self.Order.stop()
        self.technic.stop()
        self.ratio_panel_5m.stop()
        self.ratio_panel_1h.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()    
    app = ToggleableTickerApp(root)    
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
