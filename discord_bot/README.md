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
│   └── stock.py
├── config/
│   ├── __init__.py
│   └── settings.py
├── utils/
│   ├── __init__.py
│   └── helpers.py
├── main.py
├── requirements.txt
└── README.md
```

## Features

### Stock Market Commands
Real-time market data powered by Yahoo Finance API:

- `!price <ticker>`
  - Get current stock price
  - Example: `!price AAPL` → "💰 AAPL: $173.25"

- `!summary <ticker>`
  - Displays embedded message with:
    - Current Price
    - Day High/Low
    - Volume
  - Example: `!summary TSLA`

- `!history <ticker> [days]`
  - Price history and % change
  - Days: 1-30 (default: 7)
  - Shows: Price Change, Start/End Price
  - Example: `!history MSFT 14`

### General Commands
Basic utility commands:

- `!hello`
  - Greets the user
- `!ping`
  - Shows bot latency

### Fun Commands
Entertainment features:

- `!roll [NdM]`
  - Roll dice (default: 1d20)
  - Example: `!roll 2d6`
- `!flip`
  - Flip a coin
- `!rps <choice>`
  - Play Rock, Paper, Scissors

### Admin Commands
Moderation tools:

- `!clear <amount>`
  - Delete specified number of messages
  - Requires administrator permissions

## Setup Guide

### Prerequisites
- Python 3.8+
- Discord Bot Token
- Discord Server with admin privileges

### Installation
1. Clone the repository
2. Create a `.env` file:
```env
DISCORD_TOKEN=your_token_here
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Core Dependencies
```
discord.py>=2.0.0
yfinance==0.2.33
pandas
python-dotenv
```

## Configuration
Edit `config/settings.py` to customize:
- Command prefix (default: "!")
- Default embed color
- Owner IDs
- Welcome/Error messages

## Bot Permissions
Required Discord permissions:
- Send Messages
- Embed Links
- Read Message History
- Manage Messages (for admin commands)

## Error Handling
The bot includes comprehensive error handling for:
- Invalid commands/arguments
- API failures
- Permission issues
- Rate limiting
- Network errors

## Rate Limits
- Stock history limited to 30 days
- Dice rolls limited to 100 dice
- API calls optimized to prevent abuse

## Future Enhancements
Planned features:
- Stock comparison tools
- Dividend tracking
- Company news feed
- Earnings calendar
- Options chain data
- Custom alerts
- Portfolio tracking

## Contributing
Feel free to submit issues and pull requests.

## License
[MIT License](LICENSE)