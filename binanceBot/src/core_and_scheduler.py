# src/core_and_scheduler.py
from src.binance_utils import has_sufficient_balance
import sqlite3
from datetime import datetime, timezone
from binance.client import Client
from binance.exceptions import BinanceAPIException
import os
import logging
from types import SimpleNamespace
from src.telegram_notifications import notify_open, notify_close

# Configuration
DB_PATH    = os.getenv('DB_PATH', 'trades.db')

# --- Configurazione API Testnet ----------------
API_KEY    = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')
client     = Client(API_KEY, API_SECRET, testnet=True)

# Interval mapping DB -> Binance API, including 5-minute timeframe
INTERVAL_MAP = {
    'M5':    '5m',
    'H1':    '1h',
    'H4':    '4h',
    'Daily': '1d',
}

# Logger setup
tlogger = logging.getLogger('core')
tlogger.setLevel(logging.INFO)

def fetch_last_closed_candle(symbol: str, interval: str):
    api_interval = INTERVAL_MAP.get(interval, interval)
    klines = client.get_klines(symbol=symbol, interval=api_interval, limit=2)
    return klines[-1]

def auto_execute_pending():
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    # 1) Handle PENDING -> EXECUTED
    cur.execute(
        """
        SELECT id, symbol, quantity, entry_price, max_entry, take_profit, stop_loss, entry_interval, created_at
          FROM orders
         WHERE status = 'PENDING'
        """
    )
    pendings = cur.fetchall()
    tlogger.info(f"[DEBUG] auto_execute: {len(pendings)} PENDING orders")

    for order_id, symbol, qty, entry_price, max_entry, tp_price, sl_price, interval, created_at in pendings:
        # ——— Controllo saldo USDC ———
        candle = fetch_last_closed_candle(symbol, interval)
        last_close = float(candle[4])
        if max_entry is not None and last_close > float(max_entry):
           tlogger.info(f"[DEBUG] order {order_id} CANCELLED: last_close {last_close} > max_entry {max_entry}")
           cur.execute("UPDATE orders SET status='CANCELLED' WHERE id=?", (order_id,))
           conn.commit()
           continue

        quote_asset = symbol[-4:]
        required = float(entry_price) * float(qty)
        if not has_sufficient_balance(client, symbol[-4:], required):
            tlogger.error(
                f"[ERROR] Saldo insufficiente per order {order_id}: "
                f"richiesti {required:.2f} {symbol[-4:]}"
            )
            continue  # salta l'ordine
        created_dt = datetime.fromisoformat(created_at)
        if created_dt.tzinfo is None:
            created_dt = created_dt.replace(tzinfo=timezone.utc)

        candle     = fetch_last_closed_candle(symbol, interval)
        ts_candle  = datetime.fromtimestamp(candle[0] / 1000, tz=timezone.utc)
        last_close = float(candle[4])
        tlogger.info(
            f"[DEBUG] order={order_id} | created={created_dt} | ts_candle={ts_candle} | "
            f"entry={entry_price} | last_close={last_close}"
        )
        if last_close >= entry_price and ts_candle > created_dt:
            tlogger.info(f"[DEBUG] order {order_id} TRIGGERED: sending BUY & TP")
            try:
                qty_str = ('{:.8f}'.format(float(qty))).rstrip('0').rstrip('.')

                # Market BUY
                resp = client.create_order(
                    symbol=symbol,
                    side='BUY',
                    type='MARKET',
                    quantity=qty_str
                )
                executed_qty = sum(float(fill['qty']) for fill in resp['fills'])
                exec_price = float(resp['fills'][0]['price'])  # media o prima riempita
                exec_time  = datetime.now(timezone.utc).isoformat()

                # Place TP limit order
                client.create_order(
                    symbol=symbol,
                    side='SELL',
                    type='LIMIT',
                    timeInForce='GTC',
                    quantity=qty_str,
                    price=str(tp_price)
                )

                # Update DB
                cur.execute(
                    """
                    UPDATE orders
                       SET status='EXECUTED', executed_at=?, executed_price=?, quantity=?
                     WHERE id=?
                    """,
                    (exec_time, exec_price, executed_qty,  order_id)
                )
                conn.commit()
                tlogger.info(f"[EXECUTED] order {order_id} @ {exec_price}, TP placed")
                # Notifica Telegram apertura ordine
                notify_open(SimpleNamespace(
                    symbol=symbol,
                    quantity=qty,
                    entry_price=exec_price
                ))

            except BinanceAPIException as e:
                tlogger.error(f"[ERROR] Binance API exec {order_id}: {e}")
            except Exception as e:
                tlogger.error(f"[ERROR] Unexpected exec {order_id}: {e}")
        else:
            tlogger.info(f"[DEBUG] order {order_id} NOT triggered")

    # 2) Handle Stop-Loss for EXECUTED
    cur.execute(
        """
        SELECT id, symbol, quantity, stop_loss, stop_interval
          FROM orders
         WHERE status = 'EXECUTED'
        """
    )
    execs = cur.fetchall()
    tlogger.info(f"[DEBUG] auto_execute: {len(execs)} EXECUTED orders awaiting SL")

    for order_id, symbol, qty, sl_price, interval in execs:
        candle     = fetch_last_closed_candle(symbol, interval)
        last_close = float(candle[4])
        tlogger.info(f"[DEBUG SL] order={order_id} | stop_loss={sl_price} | last_close={last_close}")

        if last_close <= sl_price:
            tlogger.info(f"[DEBUG] order {order_id} SL TRIGGERED: sending SELL")
            try:
                qty_str = ('{:.8f}'.format(float(qty))).rstrip('0').rstrip('.')
                client.create_order(
                    symbol=symbol,
                    side='SELL',
                    type='MARKET',
                    quantity=qty_str
                )
                sl_time = datetime.now(timezone.utc).isoformat()

                cur.execute(
                    """
                    UPDATE orders
                       SET status='CLOSED_SL', executed_at=?, executed_price=?
                     WHERE id=?
                    """,
                    (sl_time, sl_price, order_id)
                )
                conn.commit()
                tlogger.info(f"[SL EXECUTED] order {order_id} @ {sl_price}")
                # Notifica Telegram chiusura Stop-Loss
                notify_close(SimpleNamespace(
                    symbol=symbol,
                    executed_price=sl_price,
                    status='CLOSED_SL'
                ))

            except BinanceAPIException as e:
                tlogger.error(f"[ERROR] Binance API SL {order_id}: {e}")
            except Exception as e:
                tlogger.error(f"[ERROR] Unexpected SL {order_id}: {e}")
        else:
            tlogger.info(f"[DEBUG] order {order_id} SL not triggered")

    # 3) Handle Take-Profit fills for EXECUTED
    cur.execute(
        """
        SELECT id, symbol, quantity, take_profit
          FROM orders
         WHERE status = 'EXECUTED'
        """
    )
    execs_tp = cur.fetchall()
    tlogger.info(f"[DEBUG TP] verifico TP per {len(execs_tp)} ordini EXECUTED")

    for order_id, symbol, qty, tp_price in execs_tp:
        open_orders = client.get_open_orders(symbol=symbol)
        tp_still_open = any(
            o['type']=='LIMIT' and 
            o['side']=='SELL' and 
            float(o['price']) == float(tp_price) and 
            float(o['origQty']) == float(qty)
            for o in open_orders
        )

        if not tp_still_open:
            tlogger.info(f"[DEBUG TP] order {order_id} TP filled, chiudo in DB")
            fill_time = datetime.now(timezone.utc).isoformat()
            cur.execute(
                """
                UPDATE orders
                   SET status='CLOSED_TP', executed_at=?, executed_price=?
                 WHERE id=?
                """,
                (fill_time, tp_price, order_id)
            )
            conn.commit()
            tlogger.info(f"[CLOSED_TP] order {order_id} @ {tp_price}")
            # Notifica Telegram chiusura Take-Profit
            notify_close(SimpleNamespace(
                symbol=symbol,
                executed_price=tp_price,
                status='CLOSED_TP'
            ))
        else:
            tlogger.info(f"[DEBUG TP] order {order_id} TP ancora aperto")

    conn.close()


