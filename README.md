# Stock Market Discord Bot

A comprehensive Discord bot that provides real-time stock market information along with general utility and fun commands.

## Directory Structure 
```
discord_bot/
├── cogs/
│   ├── __init__.py
│   ├── admin.py
│   ├── fun.py
│   ├── general.py
│   ├── stock.py
│   └── economy.py
├── config/
│   ├── __init__.py
│   └── settings.py
├── utils/
│   ├── __init__.py
│   ├── helpers.py
│   └── rate_limiting.py
├── data/
│   └── *_economic_events.json
├── main.py
├── requirements.txt
└── README.md
```

## Features

### Stock Market Commands
Real-time market data powered by Yahoo Finance API with built-in rate limiting and caching:

- `!price <ticker>`
  - Get current stock price
  - Example: `!price AAPL` → "💰 Apple Inc.: $173.25"
  - Cached for 5 minutes to prevent API abuse

- `!summary <ticker>`
  - Displays embedded message with:
    - Current Price
    - Day High/Low
    - Volume
  - Example: `!summary TSLA`
  - Rate limited to prevent Yahoo Finance API restrictions

- `!history <ticker> [days]`
  - Price history and % change
  - Days: 1-30 (default: 7)
  - Shows: Price Change, Start/End Price
  - Example: `!history MSFT 14`
  - Includes trend indicator (📈 or 📉)

- `!list_components [index]`
  - List tracked stocks by index and sector
  - Options: sp500, nasdaq, dow, all (default)
  - Organized view:
    - S&P 500 by sector (FAANG, Financial, Tech, etc.)
    - Additional NASDAQ-100 components
    - Additional Dow 30 components
  - Example: `!list_components sp500`

### Economic Calendar
Monthly economic events tracking:

- `