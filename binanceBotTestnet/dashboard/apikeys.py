# file: dashboard/apikeys.py
import streamlit as st
from sqlalchemy.exc import IntegrityError
from models import APIKey, Exchange

def show_apikeys_tab(tab, user, session):
    with tab:
        st.header('Gestione API Keys')
        for key in user.api_keys:
            c1,c2,c3 = st.columns([2,4,1])
            c1.write(key.exchange.name)
            c2.write(key.api_key)
            if c3.button('Elimina', key=f'del_{key.id}'):
                session.delete(key); session.commit(); st.experimental_rerun()
        with st.form('form_add'):
            st.subheader('Aggiungi API Key')
            exs = session.query(Exchange).order_by(Exchange.name).all()
            sel = st.selectbox('Exchange', exs, format_func=lambda e: e.name)
            a = st.text_input('API Key')
            s = st.text_input('Secret')
            if st.form_submit_button('Aggiungi'):
                if a and s:
                    try:
                        session.add(APIKey(user_id=user.id, exchange_id=sel.id, api_key=a, secret_key=s))
                        session.commit(); st.success('API Key aggiunta'); st.experimental_rerun()
                    except IntegrityError:
                        session.rollback(); st.error('Esiste già')
                else:
                    st.error('Campi obbligatori')
