from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from config import BOT_TOKEN, logger
from handlers import start, button_handler, store_command

def main():
    # Create the Application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("store", store_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    # Start the bot
    logger.info("Bot is starting...")
    app.run_polling()

if __name__ == '__main__':
    main()
