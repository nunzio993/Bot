import streamlit as st
import pandas as pd
import datetime
from pathlib import Path

from binance.client import Client
from src.core_and_scheduler import fetch_last_closed_candle
from symbols import SYMBOLS           # Lista dei simboli disponibili
from models import Order               # Modello SQLAlchemy per gli ordini
from src.adapters import BinanceAdapter, BybitAdapter

# Mapping timeframe -> (Binance interval, millisecondi)
INTERVAL_MAP = {
    'M5':    ('5m',    5 * 60 * 1000),
    'H1':    ('1h',    1 * 3600 * 1000),
    'H4':    ('4h',    4 * 3600 * 1000),
    'Daily': ('1d',   24 * 3600 * 1000),
}

def show_dashboard_tab(tab, user, adapters, session):
    with tab:
        st.header("Dashboard Binance Bot")

        # --- Form Nuovo Trade in sidebar ---
        st.sidebar.subheader("Nuovo Trade")
        with st.sidebar.form("trade_form", clear_on_submit=True):
            symbols_filtered = [s for s in SYMBOLS if s.endswith("USDC")]
            symbol = st.selectbox("Simbolo", symbols_filtered)
            quantity = st.number_input("Quantità", min_value=0.0, format="%.4f")
            entry_price = st.number_input("Entry Price", min_value=0.0, format="%.2f")
            max_entry = st.number_input(
                "Max Entry Price (annulla oltre)",
                min_value=entry_price,
                format="%.2f",
                help="Se la candela close > questo, il segnale verrà annullato"
            )
            entry_interval = st.selectbox("Entry Interval", list(INTERVAL_MAP.keys()))
            take_profit = st.number_input("Take Profit", min_value=0.0, format="%.2f")
            stop_loss = st.number_input("Stop Loss", min_value=0.0, format="%.2f")
            stop_interval = st.selectbox("Stop Interval", list(INTERVAL_MAP.keys()))

            submitted = st.form_submit_button("Aggiungi Trade")
            if submitted:
                # VALIDAZIONE DI BASE
                if not (stop_loss < entry_price < take_profit):
                    st.error("❌ Deve valere Stop Loss < Entry Price < Take Profit.")
                elif max_entry < entry_price:
                    st.error("❌ Max Entry deve essere ≥ Entry Price.")
                else:
                    # Controlla ultimo close
                    last_close = float(fetch_last_closed_candle(symbol, entry_interval)[4])
                    if last_close > max_entry:
                        st.error(f"❌ Candela {entry_interval} ({last_close:.2f}) > Max Entry; segnale annullato.")
                    elif last_close >= take_profit:
                        st.error(f"❌ Candela precedente {entry_interval} ({last_close:.2f}) ≥ TP; non inserito.")
                    else:
                        # Crea l'ordine
                        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
                        order = Order(
                            user_id=user.id,
                            symbol=symbol,
                            side="LONG",
                            quantity=quantity,
                            status="PENDING",
                            entry_price=entry_price,
                            max_entry=max_entry,
                            take_profit=take_profit,
                            stop_loss=stop_loss,
                            entry_interval=entry_interval,
                            stop_interval=stop_interval,
                            created_at=now
                        )
                        session.add(order)
                        session.commit()
                        st.success("✅ Trade aggiunto come PENDING")
                        st.experimental_rerun()

        # --- Visualizza Ordini Pendenti ed Eseguiti ---
        pending = session.query(Order).filter_by(user_id=user.id, status="PENDING").all()
        executed = session.query(Order).filter_by(user_id=user.id, status="EXECUTED").all()

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Ordini Pendenti")
            if not pending:
                st.write("Nessun ordine pendente.")
            else:
                df = pd.DataFrame([{
                    "ID": o.id,
                    "Simbolo": o.symbol,
                    "Qty": float(o.quantity),
                    "Entry": float(o.entry_price),
                    "TP": float(o.take_profit),
                    "SL": float(o.stop_loss),
                    "Interval": o.entry_interval
                } for o in pending])
                st.dataframe(df, use_container_width=True)

        with col2:
            st.subheader("Ordini Eseguiti")
            if not executed:
                st.write("Nessun ordine eseguito.")
            else:
                df2 = pd.DataFrame([{
                    "ID": o.id,
                    "Simbolo": o.symbol,
                    "Qty": float(o.quantity),
                    "Exec Price": float(o.executed_price or 0),
                    "Exec Time": o.executed_at
                } for o in executed])
                st.dataframe(df2, use_container_width=True)

