# file: dashboard/profile.py
import streamlit as st

def show_profile_tab(tab, user, session):
    with tab:
        st.header('Profilo Utente')
        st.write(f"**Username:** {user.username}")
        with st.form('form_pwd'):
            st.subheader('Modifica Password')
            old = st.text_input('Vecchia password', type='password')
            new = st.text_input('Nuova password', type='password')
            if st.form_submit_button('Salva'):
                st.info('Funzione da implementare')# file: dashboard/profile.py
