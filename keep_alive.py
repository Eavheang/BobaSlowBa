import asyncio
import logging
from datetime import datetime
from telegram.ext import ApplicationBuilder
from config import BOT_TOKEN, logger

async def send_keep_alive():
    try:
        app = ApplicationBuilder().token(BOT_TOKEN)\
            .connection_pool_size(1)\
            .pool_timeout(30.0)\
            .connect_timeout(30.0)\
            .read_timeout(30.0)\
            .write_timeout(30.0)\
            .build()
        
        # Get bot info (lightweight request)
        await app.bot.get_me()
        logger.info(f"Keep-alive request sent at {datetime.now()}")
        
        # Close the application
        await app.shutdown()
    except Exception as e:
        logger.error(f"Keep-alive request failed: {str(e)}")

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    # Run the keep-alive request
    asyncio.run(send_keep_alive())