import sqlite3

chat_id = input("Inserisci il chat_id Telegram del cliente: ").strip()
desc = input("Descrizione (facoltativa, es. 'Mario Cliente Demo'): ").strip()

conn = sqlite3.connect("trades.db")
try:
    conn.execute(
        "INSERT INTO telegram_subscribers (chat_id, description) VALUES (?, ?)",
        (chat_id, desc if desc else None)
    )
    conn.commit()
    print("✅ chat_id inserito correttamente.")
except sqlite3.IntegrityError:
    print("⚠️ Questo chat_id è già registrato.")
finally:
    conn.close()

