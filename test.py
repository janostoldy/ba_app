import streamlit as st

conn = st.connection("sql",type="sql")
conn.query("SELECT * FROM Files WHERE Typ = %s",params=("EIS",))
conn.session.cl