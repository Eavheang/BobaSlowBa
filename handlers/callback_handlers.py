from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import (
    logger, MENU, SWEET_LEVELS, OWNER_CHAT_ID, 
    OrderState, OrderItem, UserOrder, MAX_DRINKS_PER_ORDER,
    StoreStatus, state, PaymentMethod, ABA_PAYMENT_LINK
)
from database import save_order

# In-memory store for tracking orders
user_orders: dict[int, UserOrder] = {}

def get_user_order(user_id: int) -> UserOrder:
    if user_id not in user_orders:
        user_orders[user_id] = UserOrder()
    return user_orders[user_id]

def format_order_summary(order: UserOrder) -> str:
    summary = "🧋 *Your Order:*\n\n"
    for idx, item in enumerate(order.items, 1):
        # Escape the decimal point in price
        price_str = f"{item.price:.2f}".replace(".", "\\.")
        summary += f"{idx}\\. {item.item} \\- {item.sweetness} \\- \\${price_str}\n"
    # Escape the decimal point in total price
    total_str = f"{order.get_total_price():.2f}".replace(".", "\\.")
    summary += f"\n💰 *Total: \\${total_str}*"
    return summary

async def send_order_to_owner(context: ContextTypes.DEFAULT_TYPE, user_id: int, username: str):
    order = get_user_order(user_id)
    
    # Escape special characters for the display name
    escaped_username = username.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("]", "\\]").replace(".", "\\.").replace("(", "\\(").replace(")", "\\)").replace("`", "\\`")
    
    # Create clickable username link
    # If username starts with @, use it as is, otherwise use the user_id
    if username.startswith("@"):
        username_clean = username[1:]  # Remove @ for the URL
        # For URLs in MarkdownV2, we don't escape dots in the URL part
        username_link = f"[{escaped_username}](https://t\\.me/{username_clean})"
    else:
        username_link = f"[{escaped_username}](tg://user?id={user_id})"
    
    # Create order summary
    msg = f"📥 *New Order Received from* {username_link}\!\n\n"
    for idx, item in enumerate(order.items, 1):
        escaped_item = item.item.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("]", "\\]").replace("`", "\\`")
        escaped_sweet = item.sweetness.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("]", "\\]").replace("`", "\\`")
        price_str = f"{item.price:.2f}".replace(".", "\\.")
        msg += f"{idx}\\. `{escaped_item}` \\- `{escaped_sweet}` \\- \\${price_str}\n"
    total_str = f"{order.get_total_price():.2f}".replace(".", "\\.")
    msg += f"\n💰 *Total: \\${total_str}*"
    
    # Add payment method information
    payment_info = "💵 *Payment Method:* `Cash`" if order.payment_method == PaymentMethod.CASH else "🏦 *Payment Method:* `ABA Pay`"
    msg += f"\n{payment_info}"
    
    keyboard = [[InlineKeyboardButton("✅ Complete", callback_data=f"done_{user_id}")]]
    try:
        await context.bot.send_message(
            chat_id=OWNER_CHAT_ID,
            text=msg,
            parse_mode="MarkdownV2",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        logger.error(f"Failed to send message to owner: {str(e)}")
        # Send a simplified message as fallback
        simple_msg = f"New Order from {username}:\n"
        for idx, item in enumerate(order.items, 1):
            simple_msg += f"{idx}. {item.item} - {item.sweetness}\n"
        simple_msg += f"\nPayment: {order.payment_method}"
        await context.bot.send_message(
            chat_id=OWNER_CHAT_ID,
            text=simple_msg,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def show_payment_methods(query: Update.callback_query, order: UserOrder):
    """Show payment method selection buttons"""
    summary = format_order_summary(order)
    keyboard = [
        [
            InlineKeyboardButton("💵 Pay by Cash", callback_data="pay_cash"),
            InlineKeyboardButton("🏦 Pay by ABA", callback_data="pay_aba")
        ]
    ]
    await query.edit_message_text(
        f"{summary}\n\nPlease select your payment method:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="MarkdownV2"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data
    order = get_user_order(user_id)

    # Handle store status changes (owner only)
    if data.startswith("store_"):
        if user_id != OWNER_CHAT_ID:
            await query.edit_message_text("⛔ Sorry, only the store owner can change store status.")
            return
            
        if data == "store_open":
            state.store_status = StoreStatus.OPEN
            status_text = "🟢 Store is now OPEN"
        else:  # store_close
            state.store_status = StoreStatus.CLOSED
            status_text = "🔴 Store is now CLOSED"
            
        await query.edit_message_text(
            f"🏪 Store Status Updated\n\n{status_text}"
        )
        return

    if data == "order_now":
        # Check if store is open
        if state.store_status == StoreStatus.CLOSED:
            if query.message.photo:
                # If it's a photo message, send a new message
                await query.message.reply_text(
                    "😔 Sorry, the store is currently closed. Please try again later!"
                )
            else:
                # If it's a text message, edit it
                await query.edit_message_text(
                    "😔 Sorry, the store is currently closed. Please try again later!"
                )
            return
            
        # Show categories
        keyboard = [[InlineKeyboardButton(cat, callback_data=f"cat_{cat}")] for cat in MENU]
        if query.message.photo:
            # If the message has a photo, send a new message
            await query.message.reply_text(
                "Choose a category:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            # If it's a text message, we can edit it
            await query.edit_message_text(
                "What do you want to order?:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        order.state = OrderState.SELECTING_CATEGORY

    elif data.startswith("cat_"):
        category = data[4:]
        order.current_item = OrderItem(category=category, item=None)
        # Show items
        items = MENU[category]
        keyboard = [[InlineKeyboardButton(item, callback_data=f"item_{item}")] for item in items]
        await query.edit_message_text(f"{category} Menu:", reply_markup=InlineKeyboardMarkup(keyboard))
        order.state = OrderState.SELECTING_ITEM

    elif data.startswith("item_"):
        item = data[5:]
        order.current_item.set_item(item)
        # Show sweetness options
        keyboard = [[InlineKeyboardButton(level, callback_data=f"sweet_{level}")] for level in SWEET_LEVELS]
        await query.edit_message_text("Choose your sweetness level:", reply_markup=InlineKeyboardMarkup(keyboard))
        order.state = OrderState.SELECTING_SWEETNESS

    elif data.startswith("sweet_"):
        sweet = data[6:]
        order.current_item.sweetness = sweet
        order.add_item(order.current_item)
        
        # Show order summary and options
        summary = format_order_summary(order)
        keyboard = []
        
        # Add "Order More" button if under limit
        if order.can_add_more():
            keyboard.append([InlineKeyboardButton("🛍️ Order More", callback_data="order_more")])
        
        # Always add "Confirm Order" button
        keyboard.append([InlineKeyboardButton("✅ Confirm Order", callback_data="confirm_order")])
        
        await query.edit_message_text(
            f"{summary}\n\nWhat would you like to do?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="MarkdownV2"
        )
        order.state = OrderState.CONFIRMING_ORDER

    elif data == "order_more":
        if not order.can_add_more():
            await query.edit_message_text(
                f"You've reached the maximum limit of {MAX_DRINKS_PER_ORDER} drinks per order.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Confirm Order", callback_data="confirm_order")]])
            )
            return
            
        # Show categories again
        keyboard = [[InlineKeyboardButton(cat, callback_data=f"cat_{cat}")] for cat in MENU]
        await query.edit_message_text(
            "Choose another drink category:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        order.state = OrderState.SELECTING_CATEGORY

    elif data == "confirm_order":
        # Show payment method selection
        await show_payment_methods(query, order)
        order.state = OrderState.SELECTING_PAYMENT

    elif data.startswith("pay_"):
        payment_method = data[4:]  # Extract payment method (cash or aba)
        order.payment_method = payment_method
        
        # Send order to owner and save to database
        username = query.from_user.username or query.from_user.full_name
        
        # Save order to database
        order_items = [item.to_dict() for item in order.items]
        await save_order(
            user_id=user_id,
            username=username,
            items=order_items,
            total_amount=order.get_total_price(),
            payment_method=payment_method
        )
        
        # Send order to owner
        await send_order_to_owner(context, user_id, username)
        
        try:
            if payment_method == PaymentMethod.ABA:
                # Create clickable link using markdown
                msg = (
                    f"{format_order_summary(order)}\n\n"
                    f"Please complete your payment using this link:\n"
                    f"[Click here to pay with ABA]({ABA_PAYMENT_LINK})\n\n"
                    f"Your order will be processed after payment confirmation\\."
                )
            else:  # cash
                msg = (
                    f"{format_order_summary(order)}\n\n"
                    f"Thank you\\! Please pay in cash when picking up your order\\."
                )
            
            # For messages with photo, send new message instead of editing
            if query.message.photo:
                await query.message.reply_text(
                    msg,
                    parse_mode="MarkdownV2"
                )
            else:
                await query.edit_message_text(
                    msg,
                    parse_mode="MarkdownV2"
                )
        except Exception as e:
            logger.error(f"Error sending payment confirmation: {str(e)}")
            # Fallback message without markdown
            fallback_msg = "Thank you for your order! "
            if payment_method == PaymentMethod.ABA:
                fallback_msg += f"Please complete your payment at: {ABA_PAYMENT_LINK}"
            else:
                fallback_msg += "Please pay in cash when picking up your order."
            
            if query.message.photo:
                await query.message.reply_text(fallback_msg)
            else:
                await query.edit_message_text(fallback_msg)
        
        # Clear the order after confirmation
        order.clear()

    elif data.startswith("done_"):
        customer_id = int(data[5:])
        await context.bot.send_message(
            chat_id=customer_id,
            text="✅ Your drinks are ready! Please come and pick them up."
        )
        await query.edit_message_text("✅ Order marked as complete.") 