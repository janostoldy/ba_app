import streamlit as st
from Classes.datenbank import Database

def home_app():
    st.title("Home")
    st.divider()
    st.write("Wähle eine Anwendung aus der Seitenleiste")
    #Datenbank verbinden
    try:
        if "DB" not in st.session_state or st.session_state["DB"] is None:
            st.session_state["DB"] = Database("Eis_Analyse.db","Volumes/ge95his/Datenbank")
            st.session_state["DB"].create_table()
            st.success("Datenbank verbunden")
    except Exception as e:
        st.session_state["DB"] = None
        st.error(f"Fehler beim Verbinden mit der Datenbank: {e}")

    if "DB" not in st.session_state or st.session_state["DB"] is None:
        con1 = st.container(border=True)
        con1.header("Connect to Database")
        db_path = con1.text_input("Insert Database-Folder", placeholder="Volumes/ge95his/Datenbank",
                                  value="Volumes/ge95his/Datenbank")

        if con1.button("Datenbank verbinden", type="primary", use_container_width=True):
            try:
                st.session_state["DB"] = Database("Eis_Analyse.db",db_path)
                st.session_state["DB"].create_table()
                con1.success("Datenbank verbunden")
            except Exception as e:
                st.session_state["DB"] = None
                con1.error(f"Fehler beim Verbinden mit der Datenbank: {e}")