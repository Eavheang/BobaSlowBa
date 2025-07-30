from telegram import Update
from telegram.ext import ContextTypes
from config import OWNER_CHAT_ID

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available commands"""
    user_id = update.effective_user.id
    is_admin = user_id == OWNER_CHAT_ID
    
    # Basic commands for all users
    basic_commands = """
📱 *Available Commands*

/start \\- Start the bot and see the menu
/order \\- Start a new order

"""

    # Admin-only commands
    admin_commands = """
👑 *Admin Commands*

/store \\- Manage store status \\(open/close\\)
/sales \\- View sales reports and statistics
"""

    # Format the help message
    help_text = basic_commands
    if is_admin:
        help_text += admin_commands
        
    help_text += "\nℹ️ Use these commands to interact with the bot\\."

    await update.message.reply_text(
        help_text,
        parse_mode="MarkdownV2"
    )