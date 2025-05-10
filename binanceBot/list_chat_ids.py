import sqlite3

conn = sqlite3.connect("trades.db")
rows = conn.execute("SELECT id, chat_id, description, enabled FROM telegram_subscribers").fetchall()
conn.close()

print("👥 Utenti registrati:")
for row in rows:
    print(f"ID: {row[0]} | chat_id: {row[1]} | Descrizione: {row[2]} | Abilitato: {bool(row[3])}")

