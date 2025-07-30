from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from config import BOT_TOKEN, logger
from handlers import start, button_handler, store_command
from handlers.sales_handler import sales_command, sales_button_handler
from handlers.help_handler import help_command

def main():
    # Create the Application
    app = ApplicationBuilder().token(BOT_TOKEN)\
        .connection_pool_size(8)\
        .pool_timeout(30.0)\
        .connect_timeout(30.0)\
        .read_timeout(30.0)\
        .write_timeout(30.0)\
        .build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("store", store_command))
    app.add_handler(CommandHandler("sales", sales_command))
    app.add_handler(CommandHandler("help", help_command))
    
    # Add callback handlers
    app.add_handler(CallbackQueryHandler(sales_button_handler, pattern="^sales_"))
    app.add_handler(CallbackQueryHandler(button_handler))

    # Start the bot
    logger.info("Bot is starting...")
    app.run_polling()

if __name__ == '__main__':
    main()
