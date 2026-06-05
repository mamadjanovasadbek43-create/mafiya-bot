from telegram import InlineKeyboardButton, InlineKeyboardMarkup

OWNER_ID = 8847558918

SHOP_ITEMS = {
    'qurol': {'name': '🔫 Qurol', 'description': 'Qoshimcha oq', 'price': 30, 'currency': 'coins'},
    'bronejjilet': {'name': '🛡 Bronjejilet', 'description': 'Bir marta olimdan himoya', 'price': 50, 'currency': 'coins'},
    'dori': {'name': '💊 Dori', 'description': 'Qoshimcha davolash', 'price': 25, 'currency': 'coins'},
    'kozoynak': {'name': '🔭 Kozoynak', 'description': '2 kishini tekshirish', 'price': 40, 'currency': 'coins'},
    'bomba': {'name': '💣 Bomba', 'description': '2 kishini oldiradi', 'price': 60, 'currency': 'coins'},
    'olmos_qurol': {'name': '💎 Olmos qurol', 'description': 'Himoyani yorib otadi', 'price': 5, 'currency': 'diamonds'},
    'olmos_zirh': {'name': '💎 Olmos zirh', 'description': '3 marta himoya', 'price': 8, 'currency': 'diamonds'},
    'olmos_koz': {'name': '💎 Sehrli koz', 'description': 'Rolni toliq koradi', 'price': 10, 'currency': 'diamonds'},
}

class Shop:
    def get_keyboard(self, user_id=None):
        keyboard = []
        for item_id, item in SHOP_ITEMS.items():
            if user_id == OWNER_ID:
                icon = "💎" if item['currency'] == 'diamonds' else "🪙"
                btn = InlineKeyboardButton(f"{item['name']} — BEPUL", callback_data=f"buy_{item_id}")
            else:
                icon = "💎" if item['currency'] == 'diamonds' else "🪙"
                btn = InlineKeyboardButton(f"{item['name']} — {item['price']}{icon}", callback_data=f"buy_{item_id}")
            keyboard.append([btn])
        return InlineKeyboardMarkup(keyboard)

    def get_item(self, item_id):
        return SHOP_ITEMS.get(item_id)
