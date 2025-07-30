from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import OWNER_CHAT_ID
from database import get_sales_summary
from datetime import datetime

def escape_markdown(text: str) -> str:
    """Escape special characters for MarkdownV2 format"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f"\\{char}")
    return text

async def format_sales_summary(summary: dict) -> str:
    """Format sales summary for display"""
    if not summary:
        return "❌ Error fetching sales data"
        
    period_names = {
        'day': 'Today',
        'week': 'This Week',
        'month': 'This Month',
        'overall': 'Overall'
    }
    
    start_date = datetime.fromisoformat(summary['start_date'])
    end_date = datetime.fromisoformat(summary['end_date'])
    
    # Format dates with escaped characters
    start_date_str = escape_markdown(start_date.strftime('%Y-%m-%d'))
    end_date_str = escape_markdown(end_date.strftime('%Y-%m-%d'))
    
    msg = f"📊 *Sales Summary \\- {escape_markdown(period_names[summary['period']])}*\n"
    msg += f"_{start_date_str} to {end_date_str}_\n\n"
    
    # Format total sales with escaped characters
    total_sales = f"${summary['total_sales']:.2f}"
    msg += f"💰 *Total Sales: {escape_markdown(total_sales)}*\n"
    msg += f"📦 *Total Orders: {summary['total_orders']}*\n\n"
    
    if summary['items_sold']:
        msg += "*Top Selling Items:*\n"
        for item, quantity in summary['items_sold'].items():
            # Escape item name and format quantity
            escaped_item = escape_markdown(item)
            msg += f"• {escaped_item}: {quantity} sold\n"
    
    if 'error' in summary:
        msg += f"\n⚠️ *Error:* {escape_markdown(summary['error'])}"
    
    return msg

async def sales_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /sales command - owner only"""
    user_id = update.effective_user.id
    
    # Check if the user is the owner
    if user_id != OWNER_CHAT_ID:
        await update.message.reply_text(
            "⛔ Sorry, only the store owner can view sales data."
        )
        return
    
    # Create keyboard with period options
    keyboard = [
        [
            InlineKeyboardButton("📅 Today", callback_data="sales_day"),
            InlineKeyboardButton("📅 This Week", callback_data="sales_week")
        ],
        [
            InlineKeyboardButton("📅 This Month", callback_data="sales_month"),
            InlineKeyboardButton("📊 Overall", callback_data="sales_overall")
        ]
    ]
    
    await update.message.reply_text(
        "📊 *Sales Report*\n\nSelect the period to view:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="MarkdownV2"
    )

async def sales_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle sales report button clicks"""
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != OWNER_CHAT_ID:
        await query.edit_message_text(
            "⛔ Sorry, only the store owner can view sales data."
        )
        return
    
    # Get the selected period from callback data
    period = query.data.split('_')[1]  # sales_day -> day
    
    # Get sales summary
    summary = await get_sales_summary(period)
    
    # Format and send the summary
    msg = await format_sales_summary(summary)
    

    
    await query.edit_message_text(
        msg,
        parse_mode="MarkdownV2"
    )