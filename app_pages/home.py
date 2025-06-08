import streamlit as st
from Classes.datenbank import Database

def home_app():
    st.title("Home")
    st.divider()
    st.write("Wähle eine Anwendung aus der Seitenleiste")
    #Datenbank verbinden
    try:
        if "DB" not in st.session_state or st.session_state["DB"] is None:
            st.session_state["DB"] = Database("Formierung")
            st.success("Datenbank verbunden")
    except Exception as e:
        con1 = st.container(border=True)
        con1.error(f"Fehler beim Verbinden mit der Datenbank: {e}")
        st.session_state["DB"] = None

    try:
        DB = st.session_state["DB"]
        DB.query("SELECT * FROM Files")
    except Exception as e:
        con1 = st.container(border=True)
        st.subheader("Datenbank verbinden")
        st.error(e)
        if con1.button("Datenbank verbinden", type="primary", use_container_width=True):
            try:
                st.session_state["DB"] = Database("Formierung")
                con1.success("Datenbank verbunden")
                st.rerun()
            except Exception as e:
                st.session_state["DB"] = None