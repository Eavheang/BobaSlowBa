from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import logger, OWNER_CHAT_ID, StoreStatus, state
from .image_handler import send_menu_image

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    try:
        keyboard = [[InlineKeyboardButton("🛒 Order Now", callback_data="order_now")]]
        keyboard_markup = InlineKeyboardMarkup(keyboard)
        welcome_message = "Hi, welcome to BoBa Slow-Ba Cafe. What would you like to order?\n\nType /help to see all available commands."
        
        # Get or send menu image with welcome message and keyboard
        file_id = await send_menu_image(
            update.effective_chat.id,
            context,
            caption=welcome_message,
            reply_markup=keyboard_markup
        )
        
        if file_id:
            # Photo was sent successfully with caption and keyboard, no need to do anything else
            pass
        else:
            # Fallback if image is not available
            logger.warning("Sending welcome message without menu image")
            await update.message.reply_text(
                welcome_message,
                reply_markup=keyboard_markup
            )
    except Exception as e:
        logger.error(f"Error in start command: {str(e)}")
        await update.message.reply_text(
            "Welcome to BoBa Slow-Ba Cafe! I apologize, but I'm having trouble showing you our menu image. "
            "Please try the Order Now button below.",
            reply_markup=keyboard_markup
        )

async def store_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /store command - owner only"""
    user_id = update.effective_user.id
    
    # Check if the user is the owner
    if user_id != OWNER_CHAT_ID:
        await update.message.reply_text(
            "⛔ Sorry, only the store owner can use this command."
        )
        return

    # Create keyboard with store status options
    keyboard = [
        [
            InlineKeyboardButton("🟢 Open Store", callback_data="store_open"),
            InlineKeyboardButton("🔴 Close Store", callback_data="store_close")
        ]
    ]
    
    current_status = "🟢 Open" if state.store_status == StoreStatus.OPEN else "🔴 Closed"
    
    await update.message.reply_text(
        f"🏪 Store Status Management\n\nCurrent status: {current_status}\n\nSelect new status:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    ) 