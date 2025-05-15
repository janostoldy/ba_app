import streamlit as st

def zelle_app():
    st.title("Zellen")
    DB = st.session_state["DB"]
    con1 = st.container(border=True)
    con1.write("Zellen Filtern")

    zellen = DB.query("SELECT * FROM Zellen")
    st.dataframe(zellen)