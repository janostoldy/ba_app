import streamlit as st
from Classes.datenbank import Database

def home_app():
    st.title("Home")
    st.divider()
    st.write("Wähle eine Anwendung aus der Seitenleiste")
    con1 = st.container(border=False)
    #Datenbank Testen
    DB = Database("Home")
    time = DB.check_con()
    if time is not None:
        st.success(f"Datenbank verbunden -> Antwortzeit {time} s")
    else:
        st.error("Datenbank nicht verbunden")


