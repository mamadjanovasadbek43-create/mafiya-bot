import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from database import Database
from game import Game
from shop import Shop

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
OWNER_ID = 8847558918
db = Database()
games = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.first_name, user.username)
    await update.message.reply_text(
        f"🎭 Salom, {user.first_name}!\n\n🗡 *Mafiya Samurai* ga xush kelibsiz!\n\n"
        "📋 Buyruqlar:\n/yangioyun — Yangi o'yin\n/qoshilish — Qo'shilish\n"
        "/dokon — Do'kon\n/balans — Balans\n/yordam — Yordam",
        parse_mode="Markdown"
    )

async def yordam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎭 *MAFIYA SAMURAI — YORDAM*\n\n"
        "/yangioyun — Yangi o'yin\n/qoshilish — Qo'shilish\n"
        "/boshlash — Boshlash\n/tunguvoh — Tunni tugatish\n"
        "/rolim — Rolim\n/ovoz @username — Ovoz\n"
        "/otish @username — Otish\n/davolash @username — Davolash\n"
        "/tekshirish @username — Tekshirish\n/himoya @username — Himoya\n"
        "/sevish @username — Bloklash\n/portlatish @username — Portlatish\n\n"
        "/dokon — Do'kon\n/balans — Balans\n/transfer @username miqdor — O'tkazma\n\n"
        "*Admin:*\n/berpul @username miqdor\n/berdiamond @username miqdor",
        parse_mode="Markdown"
    )

async def balans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.first_name, user.username)
    data = db.get_user(user.id)
    await update.message.reply_text(
        f"💰 *{user.first_name} balansi:*\n\n💎 Olmos: {data['diamonds']}\n🪙 Tangalar: {data['coins']}",
        parse_mode="Markdown"
    )

async def transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("❌ /transfer @username miqdor")
        return
    username = args[0].replace("@", "")
    try:
        amount = int(args[1])
    except ValueError:
        await update.message.reply_text("❌ Miqdor son bo'lishi kerak!")
        return
    if amount <= 0:
        await update.message.reply_text("❌ Miqdor musbat bo'lishi kerak!")
        return
    sender = db.get_user(user.id)
    receiver = db.get_user_by_username(username)
    if not receiver:
        await update.message.reply_text("❌ Foydalanuvchi topilmadi!")
        return
    if user.id != OWNER_ID and sender['coins'] < amount:
        await update.message.reply_text("❌ Tangalar yetarli emas!")
        return
    db.transfer_coins(user.id, receiver['user_id'], amount)
    await update.message.reply_text(f"✅ {amount} 🪙 @{username} ga o'tkazildi!")

async def berpul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != OWNER_ID:
        await update.message.reply_text("❌ Faqat admin!")
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("❌ /berpul @username miqdor")
        return
    username = args[0].replace("@", "")
    amount = int(args[1])
    receiver = db.get_user_by_username(username)
    if not receiver:
        await update.message.reply_text("❌ Foydalanuvchi topilmadi!")
        return
    db.add_reward(receiver['user_id'], coins=amount)
    await update.message.reply_text(f"✅ {amount} 🪙 @{username} ga berildi!")

async def berdiamond(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != OWNER_ID:
        await update.message.reply_text("❌ Faqat admin!")
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("❌ /berdiamond @username miqdor")
        return
    username = args[0].replace("@", "")
    amount = int(args[1])
    receiver = db.get_user_by_username(username)
    if not receiver:
        await update.message.reply_text("❌ Foydalanuvchi topilmadi!")
        return
    db.add_reward(receiver['user_id'], diamonds=amount)
    await update.message.reply_text(f"✅ {amount} 💎 @{username} ga berildi!")

async def yangi_oyun(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if chat_id > 0:
        await update.message.reply_text("❌ Faqat guruhlarda!")
        return
    if chat_id in games and games[chat_id].status == "waiting":
        await update.message.reply_text("⚠️ O'yin kutilmoqda! /qoshilish")
        return
    db.add_user(user.id, user.first_name, user.username)
    games[chat_id] = Game(chat_id, user.id)
    games[chat_id].add_player(user.id, user.first_name, user.username)
    keyboard = [[InlineKeyboardButton("🎮 Qo'shilish", callback_data="join_game")]]
    await update.message.reply_text(
        f"🎭 *Yangi o'yin boshlandi!*\n\n👑 Yaratuvchi: {user.first_name}\n"
        f"👥 O'yinchilar: 1\n\nKamida 4 kishi kerak!\n/boshlash — boshlash",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def qoshilish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if chat_id not in games:
        await update.message.reply_text("❌ O'yin yo'q! /yangioyun")
        return
    game = games[chat_id]
    if game.status != "waiting":
        await update.message.reply_text("❌ O'yin boshlangan!")
        return
    db.add_user(user.id, user.first_name, user.username)
    result = game.add_player(user.id, user.first_name, user.username)
    if result == "already":
        await update.message.reply_text("⚠️ Allaqachon o'yindasiz!")
        return
    await update.message.reply_text(
        f"✅ *{user.first_name}* qo'shildi! 👥 Jami: {len(game.players)}",
        parse_mode="Markdown"
    )

async def join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_chat.id
    user = query.from_user
    if chat_id not in games:
        await query.answer("❌ O'yin topilmadi!", show_alert=True)
        return
    game = games[chat_id]
    if game.status != "waiting":
        await query.answer("❌ O'yin boshlangan!", show_alert=True)
        return
    db.add_user(user.id, user.first_name, user.username)
    result = game.add_player(user.id, user.first_name, user.username)
    if result == "already":
        await query.answer("⚠️ Allaqachon o'yindasiz!", show_alert=True)
        return
    await context.bot.send_message(
        chat_id,
        f"✅ *{user.first_name}* qo'shildi! 👥 Jami: {len(game.players)}",
        parse_mode="Markdown"
    )

async def boshlash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if chat_id not in games:
        await update.message.reply_text("❌ O'yin yo'q!")
        return
    game = games[chat_id]
    if game.creator_id != user.id:
        await update.message.reply_text("❌ Faqat yaratuvchi boshlaydi!")
        return
    if len(game.players) < 4:
        await update.message.reply_text(f"❌ Kamida 4 kishi kerak! Hozir: {len(game.players)}")
        return
    game.assign_roles()
    game.status = "night"
    players_list = "\n".join([f"• {p['name']}" for p in game.players.values()])
    await update.message.reply_text(
        f"🎭 *O'YIN BOSHLANDI!*\n\n👥 O'yinchilar:\n{players_list}\n\n🌙 Kecha boshlanmoqda!",
        parse_mode="Markdown"
    )
    for player_id, player in game.players.items():
        role_info = game.get_role_info(player['role'])
        try:
            await context.bot.send_message(
                player_id,
                f"🎭 *Rolingiz: {role_info['name']}*\n\n{role_info['description']}\n\n{role_info['ability']}",
                parse_mode="Markdown"
            )
        except:
            pass
    await start_night(update, context, chat_id)

async def start_night(update, context, chat_id):
    game = games[chat_id]
    game.night += 1
    game.night_actions = {}
    alive = game.get_alive_players()
    players_list = "\n".join([f"• {p['name']}" for p in alive.values()])
    await context.bot.send_message(
        chat_id,
        f"🌙 *{game.night}-KECHA*\n\n😴 Shahar uxlayapti...\n\n👥 Tiriklar:\n{players_list}\n\n"
        "🔫 Mafia/Don: /otish @username\n🔍 Detektiv: /tekshirish @username\n"
        "💊 Doktor: /davolash @username\n🎯 Snayper: /himoya @username\n"
        "💋 Fohisha: /sevish @username\n💣 Manyak: /portlatish @username\n\n"
        "Tun tugadi: /tunguvoh",
        parse_mode="Markdown"
    )

async def rolim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if chat_id not in games or user.id not in games[chat_id].players:
        await update.message.reply_text("❌ Siz bu o'yinda emassiz!")
        return
    player = games[chat_id].players[user.id]
    role_info = games[chat_id].get_role_info(player['role'])
    try:
        await context.bot.send_message(
            user.id,
            f"🎭 *Rolingiz: {role_info['name']}*\n\n{role_info['description']}\n\n{role_info['ability']}",
            parse_mode="Markdown"
        )
        await update.message.reply_text("✅ Rol shaxsiy xabarga yuborildi!")
    except:
        await update.message.reply_text("❌ Avval botga /start yozing!")

async def ovoz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if chat_id not in games:
        return
    game = games[chat_id]
    if game.status != "day":
        await update.message.reply_text("❌ Ovoz faqat kunduz!")
        return
    if not context.args:
        await update.message.reply_text("❌ /ovoz @username")
        return
    if user.id not in game.players or not game.players[user.id]['alive']:
        return
    target = game.get_player_by_username(context.args[0].replace("@", ""))
    if not target or not target['alive']:
        await update.message.reply_text("❌ Topilmadi!")
        return
    if target['id'] == user.id:
        await update.message.reply_text("❌ O'zingizga ovoz bera olmaysiz!")
        return
    game.add_vote(user.id, target['id'])
    await update.message.reply_text(
        f"🗳 *{user.first_name}* → *{target['name']}*",
        parse_mode="Markdown"
    )
    if game.check_voting_complete():
        await end_voting(update, context, chat_id)

async def end_voting(update, context, chat_id):
    game = games[chat_id]
    result = game.get_voting_result()
    if result:
        player = game.players[result]
        game.eliminate_player(result)
        role_info = game.get_role_info(player['role'])
        await context.bot.send_message(
            chat_id,
            f"⚖️ *{player['name']}* chiqarildi!\n🎭 Rol: {role_info['name']}\n\n🌙 Kecha...",
            parse_mode="Markdown"
        )
    else:
        await context.bot.send_message(chat_id, "🤝 Ovozlar teng!\n\n🌙 Kecha...", parse_mode="Markdown")
    winner = game.check_winner()
    if winner:
        await end_game(context, chat_id, winner)
    else:
        game.status = "night"
        game.votes = {}
        await start_night(update, context, chat_id)

async def otish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if chat_id not in games:
        return
    game = games[chat_id]
    if game.status != "night":
        return
    if user.id not in game.players or not game.players[user.id]['alive']:
        return
    if game.players[user.id]['role'] not in ['don', 'mafia', 'snayper']:
        await update.message.reply_text("❌ Sizning rolingiz o'q uza olmaydi!")
        return
    if not context.args:
        await update.message.reply_text("❌ /otish @username")
        return
    target = game.get_player_by_username(context.args[0].replace("@", ""))
    if not target or not target['alive']:
        await update.message.reply_text("❌ Topilmadi!")
        return
    game.add_night_action(user.id, 'shoot', target['id'])
    await update.message.reply_text("🔫 Belgilandi!")

async def davolash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if chat_id not in games:
        return
    game = games[chat_id]
    if game.status != "night" or user.id not in game.players:
        return
    if game.players[user.id]['role'] != 'doktor':
        await update.message.reply_text("❌ Faqat Doktor!")
        return
    if not context.args:
        await update.message.reply_text("❌ /davolash @username")
        return
    target = game.get_player_by_username(context.args[0].replace("@", ""))
    if not target or not target['alive']:
        await update.message.reply_text("❌ Topilmadi!")
        return
    game.add_night_action(user.id, 'heal', target['id'])
    await update.message.reply_text("💊 Belgilandi!")

async def tekshirish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if chat_id not in games:
        return
    game = games[chat_id]
    if game.status != "night" or user.id not in game.players:
        return
    if game.players[user.id]['role'] != 'detektiv':
        await update.message.reply_text("❌ Faqat Detektiv!")
        return
    if not context.args:
        await update.message.reply_text("❌ /tekshirish @username")
        return
    target = game.get_player_by_username(context.args[0].replace("@", ""))
    if not target or not target['alive']:
        await update.message.reply_text("❌ Topilmadi!")
        return
    game.add_night_action(user.id, 'check', target['id'])
    side = "🌙 MAFIA" if target['role'] in ['don', 'mafia', 'manyak', 'fohisha'] else "☀️ TINCH"
    try:
        await context.bot.send_message(user.id, f"🔍 *{target['name']}* — {side}", parse_mode="Markdown")
    except:
        pass
    await update.message.reply_text("🔍 Natija shaxsiy xabarda!")

async def himoya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if chat_id not in games:
        return
    game = games[chat_id]
    if game.status != "night" or user.id not in game.players:
        return
    if game.players[user.id]['role'] != 'snayper':
        await update.message.reply_text("❌ Faqat Snayper!")
        return
    if not context.args:
        await update.message.reply_text("❌ /himoya @username")
        return
    target = game.get_player_by_username(context.args[0].replace("@", ""))
    if not target or not target['alive']:
        await update.message.reply_text("❌ Topilmadi!")
        return
    game.add_night_action(user.id, 'protect', target['id'])
    await update.message.reply_text("🎯 Belgilandi!")

async def sevish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if chat_id not in games:
        return
    game = games[chat_id]
    if game.status != "night" or user.id not in game.players:
        return
    if game.players[user.id]['role'] != 'fohisha':
        await update.message.reply_text("❌ Faqat Fohisha!")
        return
    if not context.args:
        await update.message.reply_text("❌ /sevish @username")
        return
    target = game.get_player_by_username(context.args[0].replace("@", ""))
    if not target or not target['alive']:
        await update.message.reply_text("❌ Topilmadi!")
        return
    game.add_night_action(user.id, 'seduce', target['id'])
    await update.message.reply_text("💋 Belgilandi!")

async def portlatish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if chat_id not in games:
        return
    game = games[chat_id]
    if game.status != "night" or user.id not in game.players:
        return
    if game.players[user.id]['role'] != 'manyak':
        await update.message.reply_text("❌ Faqat Manyak!")
        return
    if not context.args:
        await update.message.reply_text("❌ /portlatish @username")
        return
    target = game.get_player_by_username(context.args[0].replace("@", ""))
    if not target or not target['alive']:
        await update.message.reply_text("❌ Topilmadi!")
        return
    game.add_night_action(user.id, 'bomb', target['id'])
    await update.message.reply_text("💣 Belgilandi!")

async def tun_tugadi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if chat_id not in games:
        return
    game = games[chat_id]
    if game.status != "night":
        await update.message.reply_text("❌ Hozir kecha emas!")
        return
    if game.creator_id != user.id:
        await update.message.reply_text("❌ Faqat yaratuvchi!")
        return
    results = game.process_night_actions()
    text = f"🌅 *{game.night}-KECHA YAKUNLANDI*\n\n"
    if results['killed']:
        for kid in results['killed']:
            p = game.players[kid]
            role_info = game.get_role_info(p['role'])
            text += f"💀 *{p['name']}* o'ldirildi! (Rol: {role_info['name']})\n"
    else:
        text += "😮 Hech kim o'lmadi!\n"
    if results.get('saved'):
        text += "💊 Doktor kimnidir qutqardi!\n"
    winner = game.check_winner()
    if winner:
        await context.bot.send_message(chat_id, text, parse_mode="Markdown")
        await end_game(context, chat_id, winner)
        return
    game.status = "day"
    game.votes = {}
    alive = game.get_alive_players()
    players_list = "\n".join([f"• {p['name']}" for p in alive.values()])
    text += f"\n☀️ *KUNDUZ!*\n\n👥 Tiriklar:\n{players_list}\n\n🗳 /ovoz @username"
    await context.bot.send_message(chat_id, text, parse_mode="Markdown")

async def end_game(context, chat_id, winner):
    game = games[chat_id]
    if winner == "mafia":
        msg = "🌙 *MAFIA G'ALABA QILDI!*\n\n"
        winners = [p for p in game.players.values() if p['role'] in ['don', 'mafia', 'manyak', 'fohisha']]
    else:
        msg = "☀️ *TINCHLAR G'ALABA QILDI!*\n\n"
        winners = [p for p in game.players.values() if p['role'] in ['tinch', 'detektiv', 'doktor', 'snayper']]
    for p in winners:
        msg += f"• {p['name']} ({game.get_role_info(p['role'])['name']})\n"
    await context.bot.send_message(chat_id, msg, parse_mode="Markdown")
    for player_id, player in game.players.items():
        if (winner == "mafia" and player['role'] in ['don', 'mafia', 'manyak', 'fohisha']) or \
           (winner == "peace" and player['role'] in ['tinch', 'detektiv', 'doktor', 'snayper']):
            db.add_reward(player_id, diamonds=10, coins=50)
        else:
            db.add_reward(player_id, diamonds=2, coins=10)
    await context.bot.send_message(chat_id, "🏆 Galiblar: 💎+10, 🪙+50\n\nYangi o'yin: /yangioyun")
    del games[chat_id]

async def dokon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.first_name, user.username)
    data = db.get_user(user.id)
    shop = Shop()
    keyboard = shop.get_keyboard(user.id)
    await update.message.reply_text(
        f"🛒 *DO'KON*\n\n💎 Olmos: {data['diamonds']}\n🪙 Tangalar: {data['coins']}\n\nTanlang:",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def shop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    item_id = query.data.replace("buy_",) 
  shop = Shop()
    item = shop.get_item(item_id)
    if not item:
        await query.answer("❌ Topilmadi!", show_alert=True)
        return
    user_data = db.get_user(user.id)
    if user.id != OWNER_ID:
        if item['currency'] == 'diamond':
            if user_data['diamonds'] < item['price']:
                await query.answer("❌ Olmoslar yetarli emas!", show_alert=True)
                return
            db.spend_diamonds(user.id, item['price'])
        else:
            if user_data['coins'] < item['price']:
                await query.answer("❌ Tangalar yetarli emas!", show_alert=True)
                return
            db.spend_coins(user.id, item['price'])
    db.add_item(user.id, item_id)
    await query.answer(f"✅ {item['name']} sotib olindi!", show_alert=True)
    keyboard = Shop().get_keyboard(user.id)
    await query.edit_message_reply_markup(reply_markup=keyboard)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("yordam", yordam))
    app.add_handler(CommandHandler("balans", balans))
    app.add_handler(CommandHandler("transfer", transfer))
    app.add_handler(CommandHandler("berpul", berpul))
    app.add_handler(CommandHandler("berdiamond", berdiamond))
    app.add_handler(CommandHandler("yangioyun", yangi_oyun))
    app.add_handler(CommandHandler("qoshilish", qoshilish))
    app.add_handler(CommandHandler("boshlash", boshlash))
    app.add_handler(CommandHandler("tunguvoh", tun_tugadi))
    app.add_handler(CommandHandler("rolim", rolim))
    app.add_handler(CommandHandler("ovoz", ovoz))
    app.add_handler(CommandHandler("otish", otish))
    app.add_handler(CommandHandler("davolash", davolash))
    app.add_handler(CommandHandler("tekshirish", tekshirish))
    app.add_handler(CommandHandler("himoya", himoya))
    app.add_handler(CommandHandler("sevish", sevish))
    app.add_handler(CommandHandler("portlatish", portlatish))
    app.add_handler(CommandHandler("dokon", dokon))
    app.add_handler(CallbackQueryHandler(join_callback, pattern="^join_game$"))
    app.add_handler(CallbackQueryHandler(shop_callback, pattern="^buy_"))
    app.run_polling()

if __name__ == "__main__":
