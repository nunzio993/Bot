import asyncio
import sqlite3
import os
from telegram import Bot
from telegram.constants import ParseMode

def get_all_chat_ids():
    conn = sqlite3.connect("/app/trades.db")
    rows = conn.execute("SELECT chat_id FROM telegram_subscribers WHERE enabled=1").fetchall()
    conn.close()
    return [r[0] for r in rows]

def send_to_all(text):
    bot = Bot(token=os.getenv("TG_BOT_TOKEN"))
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for chat_id in get_all_chat_ids():
        print(f"📤 Inviando a {chat_id}")
        try:
            loop.run_until_complete(
                bot.send_message(chat_id=chat_id, text=text, parse_mode=ParseMode.MARKDOWN)
            )
        except Exception as e:
            print(f"❌ Errore con {chat_id}: {e}")

if __name__ == "__main__":
    send_to_all("🚀 *TEST MESSAGGIO* dal bot a tutti gli iscritti")

