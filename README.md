# Stock Market Discord Bot

A comprehensive Discord bot that provides real-time stock market information, earnings reports, and economic event tracking.

## Directory Structure 
```
discord_bot/
├── cogs/
│   ├── __init__.py
│   ├── economy.py
│   ├── reports.py
│   └── stock.py
├── data/
│   └── *_economic_events.json
├── scripts/
│   ├── daily_report.py
│   └── weekly_report.py
├── utils/
│   ├── __init__.py
│   ├── forex_cache.py
│   └── forex_scraper.py
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

### Economic Calendar & Reports
Comprehensive economic event tracking and automated reports:

- `!econ_events [timeframe]`
  - View economic events for specified timeframe
  - Options: day, week (default), month
  - Shows event importance: 🔴 High, 🟡 Medium, ⚫ Low
  - Includes event times and descriptions

- `!earnings [timeframe]`
  - View earnings calendar for major index companies
  - Options: day, week (default), month
  - Shows company name, ticker, and estimated EPS
  - Filtered for S&P 500, NASDAQ-100, and Dow 30 components

### Automated Daily & Weekly Reports
The bot automatically generates and sends comprehensive market reports:

- **Daily Reports** (Monday-Friday)
  - 🌟 Market Report header with current date
  - 📊 Earnings Report section (green themed)
  - 🗓️ Economic Events section (green themed)
  - Clean divider line for readability

- **Weekly Reports** (Every Monday)
  - Same format as daily reports but with weekly outlook
  - Shows all earnings and economic events for the week ahead

### Index Components
Track major market indices:

- `!components`
  - Shows number of tracked companies across indices:
    - S&P 500 components
    - Additional NASDAQ-100 components
    - Additional Dow 30 components

## Known Issues

### Forex Factory Scraper
⚠️ The ForexFactory.com scraper is currently non-functional due to:
- Website's anti-bot measures
- Cloudflare protection
- Dynamic content loading challenges

The economic events are now stored in static JSON files in the `data` directory as a workaround.

## GitHub Actions
- Automated report generation runs Monday-Friday at 10:00 UTC (6 AM Eastern)
- Weekly reports on Mondays
- Daily reports Tuesday-Friday
- Requires `DISCORD_TOKEN` and `DISCORD_CHANNEL_ID` secrets

## Setup
1. Clone the repository
2. Install requirements: `pip install -r requirements.txt`
3. Set environment variables:
   - `DISCORD_TOKEN`: Your Discord bot token
   - `DISCORD_CHANNEL_ID`: Channel ID for automated reports
   - `ALPHA_VANTAGE_API_KEY`: For earnings data (optional)
   - The following keys are are free to create.
4. Run the bot: `python main.py` 