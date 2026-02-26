import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from keep_alive import keep_alive

# SECURITY: We use os.environ so your keys aren't visible on GitHub
ZYLA_API_KEY = os.environ.get('ZYLA_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

BASE_URL = "https://zylalabs.com/api/1813/virtual+phone+number+generator+api"
HEADERS = {"Authorization": f"Bearer {ZYLA_API_KEY}"}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        res = requests.get(f"{BASE_URL}/1466/get+countries", headers=HEADERS).json()
        if not res.get('success'):
            await update.message.reply_text("❌ API Error. Ensure you are subscribed on ZylaLabs.")
            return

        keyboard = [[InlineKeyboardButton(f"🌍 {c['countryName'].strip()}", 
                    callback_data=f"c_{c['countryCode']}")] for c in res.get('data', [])[:10]]
        
        await update.message.reply_text("👋 Select a country:", reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        await update.message.reply_text(f"Connection error: {e}")

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("c_"):
        c_code = query.data.split("_")[1]
        res = requests.get(f"{BASE_URL}/1467/get+number+by+country+id?countryCode={c_code}", headers=HEADERS).json()
        if res.get('success') and res.get('data'):
            num = res['data'][0]
            kb = [[InlineKeyboardButton("📩 Check SMS", callback_data=f"sms_{c_code}_{num}")]]
            await query.edit_message_text(f"✅ Number: `+{num}`\n\nClick below to check for SMS.", 
                                          reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

    elif query.data.startswith("sms_"):
        _, c_code, num = query.data.split("_")
        sms_res = requests.get(f"{BASE_URL}/1469/check+sms+history?countryCode={c_code}&phoneNumber={num}", headers=HEADERS).json()
        text = "⏳ No SMS found yet."
        if sms_res.get('success') and sms_res.get('data'):
            msg = sms_res['data'][0]
            text = f"📩 **From:** {msg['from']}\n**Text:** `{msg['text']}`"
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Refresh", callback_data=f"sms_{c_code}_{num}")]]), parse_mode="Markdown")

if __name__ == "__main__":
    keep_alive()
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.run_polling()
