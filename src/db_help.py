import streamlit as st

def check_db(DB):
    if DB is None:
        st.error("Keine Verbindung zur Datenbank")
        with st.sidebar:
            st.error("Keine Verbindung zur Datenbank")
        st.stop()