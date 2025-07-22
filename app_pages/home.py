import streamlit as st
from Classes.datenbank import Database

def home_app():
    st.title("Home")
    st.divider()
    st.write("Wähle eine Anwendung aus der Seitenleiste")
    con1 = st.container(border=False)
    #Datenbank Testen
    DB = Database("Home")
    try:
        time = DB.check_con()
        st.success(f"Datenbank verbunden -> Antwortzeit {time} s")
    except Exception as e:
        st.error(f"Datenbank nicht verbunden -> {e}")


