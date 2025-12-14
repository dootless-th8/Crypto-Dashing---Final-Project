import tkinter as tk
from tkinter import ttk
import websocket
import json
import threading
import requests


from collections import deque


class OrderBookPanel:
    def __init__(self, parent, symbol, greater_one):
        self.parent = parent
        self.symbol = symbol        
        self.is_active = False
        self.ws = None
        self.greater_one = greater_one
        self.first_mark = True

        self.best_bid = 0.0
        self.best_asks = 0.0
        self.spread = 0.0

        self._latest_bids = None
        self._latest_asks = None

        self._ui_job = None
        self._ui_interval = 250  # ms
        self._generation = 0

        
        style = ttk.Style()
        style.configure('TFrame', background='gray11')       # Setting the bg
        style.configure('Fra1.TFrame',background='gray30')        # Setting the elements bg
        style.configure('Fra2.TFrame',background='CadetBlue4')        # Setting the elements bg
        style.configure('Fra3.TFrame',background='MistyRose4')        # Setting the elements bg
                
        hed_bg = 'MistyRose4'
        lab_bg ='CadetBlue4'
        
        # The second-top panel
        le_frame = ttk.Frame(greater_one, relief="solid", borderwidth=1, padding=20, style='Fra1.TFrame')
        le_frame.grid(row=0, column=1, columnspan=1, sticky='nwe')

        # Heads-up
        bas_frm = ttk.Frame(le_frame, style='Fra1.TFrame')
        bas_frm.pack(fill=tk.X, expand=True, anchor=tk.CENTER)
        tk.Label(bas_frm, anchor='nw', text='Best Bid / Ask & Spread', font=("Arial", 10), background='gray19').pack(side=tk.LEFT, anchor='nw', pady=10)


        con_bas_frm = ttk.Frame(le_frame, style='Fra1.TFrame')
        con_bas_frm.pack(fill=tk.X, expand=True, anchor=tk.CENTER)

        tk.Label(con_bas_frm, anchor='nw', text='BID (Buy)', font=("Arial", 10),foreground='pale green', background='gray19').pack(side=tk.LEFT, padx=10)        
        self.BIDS_show = tk.Label(con_bas_frm, anchor='nw', text='self.best_bid', font=("Arial", 15),foreground='pale green', background='gray19')
        self.BIDS_show.pack(side=tk.LEFT, padx=10)


        tk.Label(con_bas_frm, anchor='nw', text='|', font=("Arial", 20),foreground='MediumOrchid4', background='gray19').pack(side=tk.LEFT)


        tk.Label(con_bas_frm, anchor='nw', text='ASK (Sell)', font=("Arial", 10),foreground='brown2', background='gray19').pack(side=tk.LEFT, padx=10)        
        self.ASK_show = tk.Label(con_bas_frm, anchor='nw', text='self.best_asks', font=("Arial", 15),foreground='brown2', background='gray19')
        self.ASK_show.pack(side=tk.LEFT, padx=10)

        tk.Label(con_bas_frm, anchor='nw', text='Spread', font=("Arial", 10), foreground='tan2', background='gray19').pack(side=tk.LEFT, padx=10)        
        self.spr_show = tk.Label(con_bas_frm, anchor='nw', text='self.spread', font=("Arial", 15),foreground='tan2', background='gray19')
        self.spr_show.pack(side=tk.LEFT, padx=10)



        # Creat bg panel
        self.main_frame = ttk.Frame(parent, relief="solid", borderwidth=1, padding=10, style='Fra3.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.header_frame = ttk.Frame(self.main_frame, style='Fra3.TFrame')
        self.header_frame.pack(fill=tk.X)

        # Set-up grid for headers
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=1)

        self.bids_label = ttk.Label(self.header_frame, 
                  text="BIDS (Buys - Highest to Lowest Price)", 
                  font=("Arial", 14, "bold"),
                  anchor="center",
                  foreground='lawn green',
                  background=hed_bg
                  )
        self.bids_label.grid(row=0, column=0, sticky='nsew', pady=5, padx=5)

        self.asks_label = ttk.Label(self.header_frame, 
                  text="ASKS (Sells - Lowest to Highest Price)",
                  font=("Arial", 14, "bold"),
                  anchor="center",
                  foreground='red',                  
                  style='Text_bg.TLabel',
                  background=hed_bg
                  )
        self.asks_label.grid(row=0, column=1, sticky='nsew', pady=5, padx=5)


        

      
        # ---------- #
        # First      #
        # ---------- #
        self.frame = ttk.Frame(self.main_frame, relief="solid", borderwidth=1, padding=10, style='Fra2.TFrame')        
        self.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # self.frame.grid_columnconfigure(0, weight=1)
        # self.frame.grid_columnconfigure(1, weight=1)
        # self.frame.grid_rowconfigure(0, weight=1)
        # self.frame.grid_rowconfigure(1, weight=1)


        pr_qu_frm_1_L = ttk.Frame(self.frame, style='Fra2.TFrame')
        pr_qu_frm_1_L.pack(fill=tk.X)

        p_bold = tk.Label(pr_qu_frm_1_L, anchor='w',text="Price", font=("Arial", 12, "bold"), background=lab_bg)
        # self.p_bold.grid(row=0, column=0, sticky='nw')
        p_bold.pack(side=tk.LEFT)

        q_bold = tk.Label(pr_qu_frm_1_L, text="Quantity", font=("Arial", 12, "bold"), background=lab_bg)
        # self.q_bold.grid(row=0, column=1, sticky='ne')
        q_bold.pack(side=tk.RIGHT)

        
        
        pr_qu_frm_1_R = ttk.Frame(self.frame, style='Fra2.TFrame')
        pr_qu_frm_1_R.pack(fill=tk.X)

        self.price_label_1 = tk.Label(pr_qu_frm_1_R, text="-----", font=("Arial", 10, "bold"), background=lab_bg)
        # self.price_label_1.grid(row=1, column=0, sticky='nw')
        # self.price_label_1.configure(bg='azure')
        self.price_label_1.pack(side=tk.LEFT, pady=10)
        # self.price_label.grid(row=0, column=0, sticky="E", padx=5, pady=10)

        self.quant_1 = tk.Label(pr_qu_frm_1_R, text="-----", font=("Arial", 10, "bold"), background=lab_bg)
        # self.quant_1.grid(row=1, column=1, sticky='ne')
        # self.quant_1.configure(bg='azure')
        self.quant_1.pack(side=tk.RIGHT,pady=10)        



        # ---------- #
        # Second     #
        # ---------- #
        self.frame2 = ttk.Frame(self.main_frame, relief="solid", borderwidth=1, padding=10, style='Fra2.TFrame')         
        self.frame2.pack(side=tk.RIGHT,fill=tk.BOTH, expand=True)
        
        # self.frame2.grid_columnconfigure(0, weight=1)
        # self.frame2.grid_columnconfigure(1, weight=1)
        # self.frame2.grid_rowconfigure(0, weight=1)
        # self.frame2.grid_rowconfigure(1, weight=1)

        pr_qu_frm_2_L = ttk.Frame(self.frame2, style='Fra2.TFrame')
        pr_qu_frm_2_L.pack(fill=tk.X)

        p_bold_2 = tk.Label(pr_qu_frm_2_L, anchor='w',text="Price", font=("Arial", 12, "bold"), background=lab_bg)
        p_bold_2.pack(side=tk.LEFT)
        # self.p_bold_2.grid(row=0, column=0, sticky='nw')

        q_bold_2 = tk.Label(pr_qu_frm_2_L, text="Quantity", font=("Arial", 12, "bold"), background=lab_bg)
        q_bold_2.pack(side=tk.RIGHT)
        # self.q_bold_2.grid(row=0, column=1, sticky='ne')



        pr_qu_frm_2_R = ttk.Frame(self.frame2, style='Fra2.TFrame')
        pr_qu_frm_2_R.pack(fill=tk.X)

        self.price_label_2 = tk.Label(pr_qu_frm_2_R, text="-----", font=("Arial", 10, "bold"), background=lab_bg)
        # self.price_label_2.grid(row=1, column=0, sticky='nw')
        # self.price_label_2.configure(bg='azure')
        self.price_label_2.pack(side=tk.LEFT, pady=10)
        

        self.quant_2 = tk.Label(pr_qu_frm_2_R, text="-----", font=("Arial", 10, "bold"), background=lab_bg)
        # self.quant_2.grid(row=1, column=1, sticky='ne')
        # self.quant_2.configure(bg='azure')
        self.quant_2.pack(side=tk.RIGHT,pady=10)        
        

        

    def on_message(self, ws, message):
        if not self.is_active:
            return

        try:
            data = json.loads(message)
            self._latest_bids = data["bids"][:10]
            self._latest_asks = data["asks"][:10]
        except Exception:
            return
        

    def _ui_loop(self, gen):
        if not self.is_active or gen != self._generation:
            return

        if self._latest_bids and self._latest_asks:
            bids = self._latest_bids
            asks = self._latest_asks

            b_P = "\n".join(f"{float(p):.2f}" for p, _ in bids)
            b_Q = "\n".join(f"{float(q):.4f}" for _, q in bids)
            a_P = "\n".join(f"{float(p):.2f}" for p, _ in asks)
            a_Q = "\n".join(f"{float(q):.4f}" for _, q in asks)

            best_bid = float(bids[0][0])
            best_ask = float(asks[0][0])
            spread = f"{abs(best_bid - best_ask):,.4f}"

            # 👇 SAME LABELS YOU ALREADY HAVE
            self.BIDS_show.config(text=f"{best_bid:,}")
            self.ASK_show.config(text=f"{best_ask:,}")
            self.spr_show.config(text=spread)

            self.price_label_1.config(text=b_P, fg="white")
            self.quant_1.config(text=b_Q, fg="white")
            self.price_label_2.config(text=a_P, fg="white")
            self.quant_2.config(text=a_Q, fg="white")

        self._ui_job = self.parent.after(
            self._ui_interval,
            lambda: self._ui_loop(gen)
        )



    def set_symbol(self, symbol):
        self.stop()
        self.symbol = symbol.lower()
        self.start()


    def start(self):
        if self.is_active:
            return

        self.is_active = True
        self._generation += 1
        gen = self._generation

        ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol.lower()}@depth10@100ms"

        def on_error(ws, e):
            if not self.is_active:
                return
            
            if 'sock' in str(e):
                return
            
            print("OrderBook error:", e)

        def on_close(ws, *args):
            pass  # silent close

        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self.on_message,
            on_error=on_error,
            on_close=on_close
        )

        threading.Thread(target=self.ws.run_forever, daemon=True).start()

        # start controlled UI refresh
        self._ui_loop(gen)


    def stop(self):
        if not self.is_active:
            return
        
        self.is_active = False
        self._generation += 1
        
        ws = self.ws
        self.ws = None
        
        if self._ui_job:
            self.parent.after_cancel(self._ui_job)
            self._ui_job = None

        if ws:
            try:
                ws.close()
            except Exception:
                pass
    

    def update_display(self, b_P, b_Q, a_P, a_Q):
        """Update the ticker display."""
        if not self.is_active:
            return
        
        
        # 
        self.best_bid = float(b_P.split('\n', 1)[0]) 
        # print(b_P.split('\n', 1)[0])
        self.best_asks = float(a_P.split('\n', 1)[0])       
        self.first_mark = False
        self.spread = f'{abs(self.best_bid - self.best_asks):,.4f}'

        
        self.BIDS_show.config(text=f'{self.best_bid:,}')
        self.ASK_show.config(text=f'{self.best_asks:,}')
        self.spr_show.config(text=self.spread)

        self.price_label_1.config(text=b_P, fg="white")        
        self.quant_1.config(text=b_Q, fg="white")


        self.price_label_2.config(text=a_P, fg="white")
        self.quant_2.config(text=a_Q, fg="white")
        # self.change_label.config(
        #     text=f"{sign}{change:,.2f} ({sign}{percent:.2f}%)",
        #     foreground=color
        # )
    

    # Might have to look at it later
    def pack(self, **kwargs):
        """Allow easy placement of ticker."""
        self.frame.pack(**kwargs)
    
    def pack_forget(self):
        """Hide the ticker."""
        self.frame.pack_forget()

