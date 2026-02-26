import streamlit as st
import os
import asyncio
import threading
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- CONFIGURATION ---
# Set these in Streamlit Cloud under Settings -> Secrets
ZYLA_API_KEY = st.secrets.get("ZYLA_API_KEY", "YOUR_KEY_HERE")
TELEGRAM_TOKEN = st.secrets.get("TELEGRAM_TOKEN", "YOUR_TOKEN_HERE")
BASE_URL = "https://zylalabs.com/api/1813/virtual+phone+number+generator+api"
HEADERS = {"Authorization": f"Bearer {ZYLA_API_KEY}"}

# --- BOT LOGIC ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = requests.get(f"{BASE_URL}/1466/get+countries", headers=HEADERS).json()
    if res.get('success'):
        keyboard = [[InlineKeyboardButton(f"🌍 {c['countryName'].strip()}", 
                    callback_data=f"c_{c['countryCode']}")] for c in res.get('data', [])[:10]]
        await update.message.reply_text("Select a country:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("c_"):
        c_code = query.data.split("_")[1]
        res = requests.get(f"{BASE_URL}/1467/get+number+by+country+id?countryCode={c_code}", headers=HEADERS).json()
        if res.get('success') and res.get('data'):
            num = res['data'][0]
            kb = [[InlineKeyboardButton("📩 Check SMS", callback_data=f"sms_{c_code}_{num}")]]
            await query.edit_message_text(f"✅ Number: `+{num}`", reply_markup=InlineKeyboardMarkup(kb))

# --- STREAMLIT UI ---
st.title("🤖 Bot Control Center")
st.write("The Telegram Bot is running in the background.")

# --- THREADING FIX ---
def run_bot():
    # This function runs the bot in a separate background thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.run_polling()

if "bot_started" not in st.session_state:
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()
    st.session_state.bot_started = True
    st.success("Bot started successfully!")
