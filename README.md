# BoBa Slow-Ba Telegram Bot

A Telegram bot for managing orders at BoBa Slow-Ba cafe. Customers can browse the menu, place orders, and choose payment methods, while owners can manage store status and handle orders.

## Features

- 📋 Digital Menu with Categories
  - Coffee
  - Matcha
  - Soda

- 🛍️ Order Management
  - Multiple drinks per order (up to 4)
  - Customizable sweetness levels
  - Order summary and confirmation

- 💳 Payment Options
  - Cash payment
  - ABA payment integration

- 👨‍💼 Owner Features
  - Store open/close management
  - Order notifications
  - Order completion tracking

## Setup

1. Clone the repository:
```bash
git clone https://github.com/Eavheang/BobaSlowBa.git
cd BobaSlowBa
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Create a `.env` file with your configuration:
```env
BOT_TOKEN=your_telegram_bot_token
OWNER_CHAT_ID=your_telegram_user_id
```

4. Run the bot:
```bash
python main.py
```

## Project Structure

```
BobaCafe/
├── config.py           # Configuration and constants
├── main.py            # Main entry point
├── menu.jpg           # Menu image
├── handlers/          # Handler modules
│   ├── __init__.py   # Package initialization
│   ├── command_handlers.py    # Command handlers
│   ├── callback_handlers.py   # Callback handlers
│   └── image_handler.py       # Image handling
└── requirements.txt   # Project dependencies
```

## Commands

- `/start` - Start the bot and show menu
- `/store` - (Owner only) Manage store open/close status

## Contributing

Feel free to open issues or submit pull requests if you have suggestions for improvements.

## License

MIT License
