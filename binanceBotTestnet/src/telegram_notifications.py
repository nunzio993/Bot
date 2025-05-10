# src/telegram_notifications.py
import os
import asyncio
from telegram import Bot
from telegram.constants import ParseMode

# Carica token del bot e ID chat dal file .env
BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TRY_CHAT_ID = os.getenv("TG_CHAT_ID")

# Validazione token e chat ID
if not BOT_TOKEN:
    raise ValueError("TG_BOT_TOKEN non trovato in .env")
try:
    CHAT_ID = int(TRY_CHAT_ID)
except (TypeError, ValueError):
    raise ValueError("TG_CHAT_ID non valido o non trovato in .env")

# Inizializza il Bot (asincrono)
bot = Bot(token=BOT_TOKEN)

# Helper per mandare messaggi in modo sincrono
def _send_message_sync(chat_id, text, parse_mode=None):
    return asyncio.run(bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode))


def notify_open(order):
    """
    Invia una notifica Telegram quando viene aperto un ordine.
    """
    msg = (
        "🟢 *Apertura ordine*\n"
        f"Simbolo: `{order.symbol}`\n"
        f"Quantità: {order.quantity}\n"
        f"Prezzo di entrata: {order.entry_price}\n"
    )
    _send_message_sync(chat_id=CHAT_ID, text=msg, parse_mode=ParseMode.MARKDOWN)


def notify_close(order):
    """
    Invia una notifica Telegram quando un ordine viene chiuso.
    """
    if order.status == "CLOSED_TP":
        icon = "🎯 TP"
    elif order.status == "CLOSED_SL":
        icon = "❌ SL"
    else:
        icon = "⚡️ Market"

    profit = None
    try:
        profit = float(order.executed_price) - float(order.entry_price)
    except Exception:
        pass

    msg = (
        f"🔴 *Chiusura ordine* ({icon})\n"
        f"Simbolo: `{order.symbol}`\n"
        f"Prezzo esecuzione: {order.executed_price}\n"
    )
    if profit is not None:
        msg += f"Profit/Loss: {profit:.2f}\n"

    _send_message_sync(chat_id=CHAT_ID, text=msg, parse_mode=ParseMode.MARKDOWN)

