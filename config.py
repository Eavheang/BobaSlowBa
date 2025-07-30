from pathlib import Path
from dotenv import load_dotenv
import os
import logging
from typing import Dict, List

# Load environment variables
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_CHAT_ID = int(os.getenv("OWNER_CHAT_ID"))

# Store Configuration
class StoreStatus:
    OPEN = "open"
    CLOSED = "closed"

class PaymentMethod:
    CASH = "cash"
    ABA = "aba"

# ABA Payment Configuration
ABA_PAYMENT_LINK = "https://link.payway.com.kh/ABAPAYz6370245E"

class GlobalState:
    def __init__(self):
        self.store_status = StoreStatus.CLOSED

# Global state instance
state = GlobalState()

# Logging Configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Order Configuration
MAX_DRINKS_PER_ORDER = 4

# Menu Configuration
MENU = {
    "Coffee": ["Americano", "Iced Latte", "Hot Latte", "Milked Coffee"],
    "Matcha": ["Matcha Latte", "Matcha Espresso", "Strawberry Matcha"],
    "Soda": ["Strawberry Soda", "Blueberry Soda", "Passion Soda"]
}

SWEET_LEVELS = ["More sweet", "Normal sweet", "Less sweet", "No sweet"]

# Order States
class OrderState:
    SELECTING_CATEGORY = "selecting_category"
    SELECTING_ITEM = "selecting_item"
    SELECTING_SWEETNESS = "selecting_sweetness"
    SELECTING_PAYMENT = "selecting_payment"
    CONFIRMING_ORDER = "confirming_order"

# Order structure
class OrderItem:
    def __init__(self, category: str, item: str, sweetness: str = None):
        self.category = category
        self.item = item
        self.sweetness = sweetness

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "item": self.item,
            "sweetness": self.sweetness
        }

    def __str__(self) -> str:
        return f"{self.item} ({self.sweetness})"

class UserOrder:
    def __init__(self):
        self.items: List[OrderItem] = []
        self.current_item: OrderItem = None
        self.state: str = OrderState.SELECTING_CATEGORY
        self.payment_method: str = None

    def add_item(self, item: OrderItem):
        self.items.append(item)
        self.current_item = None

    def can_add_more(self) -> bool:
        return len(self.items) < MAX_DRINKS_PER_ORDER

    def get_total_items(self) -> int:
        return len(self.items)

    def clear(self):
        self.items.clear()
        self.current_item = None
        self.state = OrderState.SELECTING_CATEGORY
        self.payment_method = None

# File paths
BASE_DIR = Path(__file__).resolve().parent
MENU_IMAGE_PATH = BASE_DIR / "menu.jpg" 