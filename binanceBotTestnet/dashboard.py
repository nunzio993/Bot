import os
import streamlit as st
from pathlib import Path
import datetime
import logging
import ccxt
from binance.client import Client
from binance.exceptions import BinanceAPIException
from sqlalchemy.exc import IntegrityError
import yaml
from models import init_db, SessionLocal, User, Exchange, APIKey, Order
import pandas as pd
from src.core_and_scheduler import auto_execute_pending, fetch_last_closed_candle
from src.binance_utils import has_sufficient_balance
from symbols import SYMBOLS  # Lista dei simboli disponibili

# Mapping timeframe -> (Binance interval, millisecondi)
INTERVAL_MAP = {
    'M5':    ('5m',    5 * 60 * 1000),
    'H1':    ('1h',    1 * 3600 * 1000),
    'H4':    ('4h',    4 * 3600 * 1000),
    'Daily': ('1d',   24 * 3600 * 1000),
}


init_db()

session = SessionLocal()


# Utility per refresh sicuro della pagina
def safe_rerun():
    try:
        st.experimental_rerun()
    except AttributeError:
        st.write("↻ Ricarica la pagina per aggiornamenti")

# Configurazione pagina
st.set_page_config(page_title='Binance Scheduler', layout='wide')

# Carica config credenziali per streamlit_authenticator
with open("credentials.yaml") as file:
    config = yaml.safe_load(file)

# Autenticazione
import streamlit_authenticator as stauth
auth = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

auth.login(location='main', key='Login')
if not st.session_state.get('authentication_status'):
    st.warning("🔒 Inserisci username e password")
    st.stop()

# Sincronizza utente
session = SessionLocal()
env_username = st.session_state.get('username')
user = session.query(User).filter_by(username=env_username).first()
if user is None:
    user = User(username=env_username, password_hash='')
    session.add(user)
    session.commit()
    user = session.query(User).filter_by(username=env_username).first()

# Barra menu con tabs
tabs = st.tabs(["Dashboard", "Profilo", "API Keys"])

# Tab Profilo
with tabs[1]:
    st.header("Profilo Utente")
    st.write(f"**Username:** {user.username}")
    # Form modifica password
    with st.form("form_pwd"):
        st.subheader("Modifica Password")
        old_pwd = st.text_input("Vecchia password", type="password")
        new_pwd = st.text_input("Nuova password", type="password")
        if st.form_submit_button("Salva"):  # placeholder, non gestito qui
            st.info('Funzione di cambio password da implementare')


# Se l’utente non esiste ancora nel DB, crealo “al volo”
user = session.query(User).filter_by(username=env_username).first()
if user is None:
    user = User(username=env_username, password_hash="")
    session.add(user)
    session.commit()
    user = session.query(User).filter_by(username=env_username).first()

# Pulsante logout
auth.logout("Logout", "sidebar")


# Config API Testnet
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')
client = Client(API_KEY, API_SECRET, testnet=True)

# Paths
LOG_PATH = Path('logs') / 'scheduler.log'


# Tab API Keys
with tabs[2]:
    st.header("Gestione API Keys")
    st.sidebar.empty()
    # Mostra e gestisci API keys
    for key in user.api_keys:
        col1, col2, col3 = st.columns([2,4,1])
        col1.write(key.exchange.name)
        col2.write(key.api_key)
        if col3.button("Elimina", key=f"del_{key.id}"):
            session.delete(key)
            session.commit()
            st.experimental_rerun()
    with st.form('form_add_key'):
        st.subheader("Aggiungi API Key")
        exchanges = session.query(Exchange).order_by(Exchange.name).all()
        sel_ex = st.selectbox("Exchange", exchanges, format_func=lambda e: e.name)
        new_api = st.text_input("API Key")
        new_sec = st.text_input("Secret Key")
        if st.form_submit_button("Aggiungi"):
            if new_api and new_sec:
                try:
                    api = APIKey(user_id=user.id, exchange_id=sel_ex.id, api_key=new_api, secret_key=new_sec)
                    session.add(api); session.commit(); st.success("API Key aggiunta!"); st.experimental_rerun()
                except IntegrityError:
                    session.rollback(); st.error("Chiave già presente per questo exchange.")
            else:
                st.error("Compila entrambi i campi.")


# Sidebar: Saldo USDC
balances = client.get_account().get('balances', [])
usdc = next((b for b in balances if b['asset']=='USDC'), {'free':'0','locked':'0'})
st.sidebar.metric('USDC disponibile', f"{float(usdc['free']):.2f}")

# Form Trade
with st.sidebar.form('trade_form'):
    st.header('Nuovo Trade')
    symbols_filtered = [s for s in SYMBOLS if s.endswith('USDC')]
    symbol = st.selectbox('Simbolo', symbols_filtered)
    quantity = st.number_input('Quantità', min_value=0.0, format='%.4f')
    entry_price = st.number_input('Entry Price', min_value=0.0, format='%.2f')
    max_entry = st.number_input('Max Entry Price', min_value=entry_price, format='%.2f')
    entry_interval = st.selectbox('Entry Interval', list(INTERVAL_MAP.keys()))
    take_profit = st.number_input('Take Profit', min_value=0.0, format='%.2f')
    stop_loss = st.number_input('Stop Loss', min_value=0.0, format='%.2f')
    stop_interval = st.selectbox('Stop Interval', list(INTERVAL_MAP.keys()))
    if st.form_submit_button('Aggiungi Trade'):
        # validazioni...
        order = Order(
            user_id=user.id,
            symbol=symbol,
            quantity=quantity,
            side='LONG',
            status='PENDING',
            entry_price=entry_price,
            max_entry=max_entry,
            take_profit=take_profit,
            stop_loss=stop_loss,
            entry_interval=entry_interval,
            stop_interval=stop_interval
        )
        session.add(order)
        session.commit()
        st.success('Trade aggiunto come PENDING')
        safe_rerun()

# Caricamento ordini
pending = session.query(Order).filter_by(user_id=user.id, status='PENDING').all()
executed = session.query(Order).filter_by(user_id=user.id, status='EXECUTED').all()
closed = session.query(Order).filter(Order.user_id==user.id, Order.status.like('CLOSED_%')).all()




# Layout a due colonne
col1, col2 = st.columns(2)

# --- Colonna 1: Ordini Pendenti --------
with col1:
    st.subheader('Ordini Pendenti')
    if not executed:
        st.write('Nessun ordine pendente.')
    else:
        df = pending.copy()
        # Tipi numerici
        df[['quantity','entry_price','take_profit','stop_loss']] = df[['quantity','entry_price','take_profit','stop_loss']].astype(float)
        # Last Close
        df['last_close'] = df.apply(lambda o: float(fetch_last_closed_candle(o['symbol'], o['entry_interval'])[4]), axis=1)
        # Stato
        df['stato'] = df.apply(lambda o: 'Pronto' if o['last_close']>=o['entry_price'] else 'In Attesa', axis=1)
        # Valore in USDT
        df['value_usd'] = df['quantity'] * df['entry_price']
        # Selezione e rinomina colonne
        disp = df[['id','symbol','quantity','entry_price','value_usd','take_profit','stop_loss','last_close','stato']]
        disp = disp.rename(columns={
            'id':'ID','symbol':'Simbolo','quantity':'Qty','entry_price':'Entry Price',
            'value_usd':'Valore (USDT)','take_profit':'TP','stop_loss':'SL',
            'last_close':'Last Close','stato':'Stato'
        })
        # Nascondi indice e mostra
        disp = disp.reset_index(drop=True)
        st.dataframe(disp, use_container_width=True, hide_index=True)
        # Annulla Pending
        sel = st.selectbox('Annulla ID (Pending)', disp['ID'], key='cancel_pending')
        if st.button('Annulla Segnale Pending', key='btn_cancel_pending'):
            conn = sqlite3.connect(DB_PATH)
            conn.execute("UPDATE orders SET status='CLOSED_MANUAL' WHERE id=?", (int(sel),))
            conn.commit(); conn.close()
            try:
                safe_rerun()
            except AttributeError:
                st.write('↻ Ricarica pagina per aggiornamenti')

# --- Colonna 2: Ordini a Mercato -------
with col2:
    st.subheader('Ordini a mercato')
    if not executed:
        st.write('Nessun ordine a mercato.')
    else:
        df = executed.copy()
        # Tipi numerici
        df[['quantity','entry_price','executed_price']] = df[
            ['quantity','entry_price','executed_price']
        ].astype(float)
        # Formatta data di esecuzione
        df['executed_at'] = pd.to_datetime(df['executed_at'])\
            .dt.strftime('%d/%m/%Y %H:%M:%S')
        # Valore in USDT
        df['value_usd'] = df['quantity'] * df['executed_price']
        # Selezione e rinomina colonne
        disp = df[[
            'id','symbol','quantity','entry_price','value_usd',
            'entry_interval','executed_price','executed_at',
            'take_profit','stop_loss','stop_interval','status'
        ]]
        disp = disp.rename(columns={
            'id':'ID',
            'symbol':'Simbolo',
            'quantity':'Qty',
            'entry_price':'Entry Price',
            'value_usd':'Valore (USDT)',
            'entry_interval':'Interval',
            'executed_price':'Exec Price',
            'executed_at':'Exec Time',
            'take_profit':'TP',
            'stop_loss':'SL',
            'stop_interval':'SL Interval',
            'status':'Status'
        })
        disp = disp.reset_index(drop=True)
        st.dataframe(disp, use_container_width=True, hide_index=True)

        # — Annulla Eseguiti (manual close)
        sel2 = st.selectbox('Annulla ID (Eseguiti)', disp['ID'], key='cancel_exec')
        if st.button('Annulla Segnale Eseguito', key='btn_cancel_exec'):
            row = disp[disp['ID'] == sel2].iloc[0]
            symbol = row['Simbolo']
            qty_order = float(row['Qty'])
            qty_str = ('{:.8f}'.format(qty_order)).rstrip('0').rstrip('.')
            try:
                # 1) Cancella eventuali LIMIT TP aperti per questa quantità
                open_orders = client.get_open_orders(symbol=symbol)
                for o in open_orders:
                    if (
                        o['side'] == 'SELL' and
                        o['type'] == 'LIMIT' and
                        float(o['origQty']) == qty_order
                    ):
                        client.cancel_order(symbol=symbol, orderId=o['orderId'])

                # 2) Vendi a mercato la quantità sbloccata
                client.create_order(
                    symbol=symbol,
                    side='SELL',
                    type='MARKET',
                    quantity=qty_str
                )

                # 3) Aggiorna il DB
                conn = sqlite3.connect(DB_PATH)
                conn.execute(
                    "UPDATE orders SET status='CLOSED_MANUAL' WHERE id=?",
                    (int(sel2),)
                )
                conn.commit()
                conn.close()

                st.success(f"✅ Posizione {sel2} chiusa manualmente ({qty_str} {symbol[:-4]})")
                try:
                    safe_rerun()
                except AttributeError:
                    st.write("↻ Ricarica la pagina per aggiornamenti")

            except BinanceAPIException as e:
                st.error(f'Errore Binance API: {e}')
            except Exception as e:
                st.error(f'Errore generico: {e}')

# --- Sezione Trade Chiusi -------------
st.markdown('---')
st.subheader('Trade Chiusi')
if not closed:
    st.write('Nessun trade chiuso.')
else:
    df = closed.copy()
    # Formatta data di esecuzione
    df['executed_at'] = pd.to_datetime(df['executed_at']).dt.strftime('%d/%m/%Y %H:%M:%S')
    disp = df.rename(columns={
        'id':'ID','symbol':'Simbolo','quantity':'Qty','entry_price':'Entry Price',
        'entry_interval':'Interval','executed_price':'Exec Price','executed_at':'Exec Time',
        'take_profit':'TP','stop_loss':'SL','stop_interval':'SL Interval','status':'Status'
    }).reset_index(drop=True)
    st.dataframe(disp, use_container_width=True, hide_index=True)

# --- Verifica Ultime Candele ---------
st.markdown('---')
st.subheader('Verifica Ultime Candele')
vsym = st.selectbox('Simbolo', symbols_filtered)
candles = []
for nm, (tf_str, _) in INTERVAL_MAP.items():
    ohlc = ccxt.binance().fetch_ohlcv(vsym, timeframe=tf_str, limit=2)[-2]
    candles.append({
        'Interval': nm,
        'Open':  f"{ohlc[1]:.2f}",
        'High':  f"{ohlc[2]:.2f}",
        'Low':   f"{ohlc[3]:.2f}",
        'Close': f"{ohlc[4]:.2f}"
    })
df_candles = pd.DataFrame(candles).reset_index(drop=True)
st.table(df_candles)

# --- Log (ultime 100 righe) ----------
st.markdown('---')
st.subheader('Log (ultime 100)')

if Path(LOG_PATH).exists():
    lines = Path(LOG_PATH).read_text().splitlines()[-100:]
else:
    lines = [f"Log file non trovato: {LOG_PATH}"]

# st.text_area si aspetta una stringa unica o un valore=...
st.text_area(
    'Ultimi log scheduler',
    value="\n".join(lines),
    height=400
)
