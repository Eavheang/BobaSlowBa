from telegram.ext import ContextTypes
from config import logger, MENU_IMAGE_PATH

# Global variable to store the file_id
MENU_IMAGE_FILE_ID = None

async def send_menu_image(chat_id: int, context: ContextTypes.DEFAULT_TYPE, caption: str = None, reply_markup = None) -> str:
    """Send menu image and return its file_id"""
    global MENU_IMAGE_FILE_ID
    
    try:
        if MENU_IMAGE_FILE_ID:
            # If we have file_id, use it to send the photo
            try:
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=MENU_IMAGE_FILE_ID,
                    caption=caption,
                    reply_markup=reply_markup,
                    read_timeout=30,
                    write_timeout=30
                )
                return MENU_IMAGE_FILE_ID
            except Exception as e:
                logger.warning(f"Failed to send photo with file_id, trying with local file: {str(e)}")
                MENU_IMAGE_FILE_ID = None  # Reset file_id if it's invalid
    
        if not MENU_IMAGE_PATH.exists():
            logger.error(f"Menu image not found at {MENU_IMAGE_PATH.absolute()}")
            return None
                
        if MENU_IMAGE_PATH.stat().st_size == 0:
            logger.error("Menu image file is empty")
            return None
                
        with open(MENU_IMAGE_PATH, 'rb') as photo:
            try:
                message = await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=caption,
                    reply_markup=reply_markup,
                    read_timeout=30,
                    write_timeout=30
                )
                MENU_IMAGE_FILE_ID = message.photo[-1].file_id
                logger.info(f"Successfully uploaded menu image, file_id: {MENU_IMAGE_FILE_ID}")
                return MENU_IMAGE_FILE_ID
            except Exception as e:
                logger.error(f"Failed to send photo: {str(e)}")
                return None
                    
    except Exception as e:
        logger.error(f"Error handling menu image: {str(e)}")
        return None 