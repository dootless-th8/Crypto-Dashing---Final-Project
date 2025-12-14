# Crypto Dashboard (Tkinter + Binance API)

A real-time cryptocurrency dashboard built with **Python** and **Tkinter**, using **Binance WebSocket and REST APIs** to display live market data.  
This project is designed as a modular desktop application, with each market component running independently and safely.

---

## Features

- **Live Price Ticker**
  - Real-time price, change, and percentage change
  - WebSocket-based updates (low latency)

- **Order Book (Depth)**
  - Best Bid / Ask
  - Spread calculation
  - Top bids and asks updated in real time

- **Technical Analysis Panel**
  - Candlestick price chart
  - Volume chart
  - Periodic REST updates

- **Buy / Sell Volume Ratio**
  - 5-minute and 1-hour volume ratio
  - Uses Binance kline data
  - Background thread with safe UI updates

- **Symbol Switching**
  - BTC, ETH, SOL, BNB, ADA, XRP
  - All panels update together

- **Show / Hide Price Ticker**
  - Toggle the main price ticker dynamically

---

## Project Structure

```bash
|   Crypto-Dashing---Final-Project
|   ├── requirements.txt  # Dependecies
|   ├── main.py          # Application entry point & layout
|   ├── ticker.py        # Live price ticker (WebSocket)
|   ├── order_book.py    # Order book / depth panel (WebSocket)
|   ├── technical.py     # Technical analysis charts (Matplotlib)
|   ├── futures.py       # Buy/Sell volume ratio panels (REST)
|   ├── Crypto-showcase.mkv  # Video Showcase
|   ├── Figma_ui_design.png  # Png Showcasing the ui layout design
|   └── README.md        # The file you're reading
```


---

## Architecture Overview

This project follows a **panel-based architecture**:

- Each module:
  - Owns its **own UI frame**
  - Has `start()` and `stop()` lifecycle methods
  - Runs independently (thread or WebSocket)

- `main.py` acts as the **orchestrator**
  - Handles layout
  - Handles symbol switching
  - Starts / stops all panels safely

### UI Safety

- WebSocket threads **do not update Tkinter directly**
- All UI updates are scheduled using:
  - `after()` (Tkinter main thread)
- Prevents freezing and race conditions

---

## Module Responsibilities

### `main.py`
- Application entry point
- Main window and layout
- Controls:
  - Symbol switching
  - Panel visibility
  - Application startup & shutdown

### `ticker.py`
- Live price ticker
- Binance **WebSocket**
- Smooth UI updates via timed refresh loop
- Public API:
  - `start()`
  - `stop()`
  - `set_symbol()`

### `order_book.py`
- Real-time order book (depth)
- Displays:
  - Best Bid
  - Best Ask
  - Spread
  - Top bids and asks
- Binance **depth WebSocket**
- Controlled UI refresh loop

### `technical.py`
- Candlestick and volume charts
- Embedded **Matplotlib** in Tkinter
- Periodic REST polling
- Clean start / stop lifecycle

### `futures.py`
- Buy / Sell volume ratio panels
- Binance **kline REST API**
- Background thread for fetching data
- UI-safe updates via `after()`

---

## How to Run

### Requirements

Python 3.9+

Install dependencies:
```bash
pip install websocket-client requests matplotlib pandas numpy
