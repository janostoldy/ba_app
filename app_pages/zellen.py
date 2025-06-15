import streamlit as st
import pandas as pd

def add_zelle_app():
    st.title("Zellen hinzufügen")
    DB = st.session_state["DB"]
    con1 = st.container(border=True)
    col1, col2, col3 = con1.columns(3)
    id = col1.text_input("Zelle ID", placeholder="SN0001", max_chars=20)
    cycle = col2.number_input("Zelle Cycle", min_value=0, max_value=1000, value=0, step=1)
    Typ = col3.text_input("Zelle Typ", placeholder="Zellen Typ" ,max_chars=20)
    info = con1.text_area("Zelle Info", placeholder="Zelle Info", max_chars=255)
    if con1.button("Daten Hinzufügen", use_container_width=True, type="primary"):
        data = pd.DataFrame({
            "id": [id],
            "Typ": [Typ],
            "Cycle": [cycle],
            "Info": [info],
        })
        try:
            with st.spinner("Daten hinzufügen...", show_time=True):
                DB.df_in_DB(df=data,table_name="Zellen")
            st.success(f"Zelle {id} erfolgreich hinzugefügt")
            st.rerun()
        except Exception as e:
            st.error(f"Fehler beim Ausführen der SQL-Anfrage: {e}")
    zellen = DB.get_all_zells()
    st.write(zellen)

def show_zelle_app():
    st.title("Zellen")
    DB = st.session_state["DB"]
    zellen = DB.get_all_zells()
    st.write(zellen)

@st.dialog("Daten Bearbeiten",width="large")
def zellen_edit():
    st.write("Index der Zelle aus dem Dargestellten Dataframe:")
    DB = st.session_state["DB"]
    zellen_id = st.session_state["zelle_filter"]["zellen_id"]
    zellen_cycle= st.session_state["zelle_filter"]["zellen_cycle"]
    #zellen = DB.get_zellen(zellen_id,zellen_cycle)
    num = st.number_input("Index", min_value=0, max_value=len(zellen), value=0, step=1)

    st.write("Daten der Zelle:")
    zelle = zellen.iloc[num]
    col1, col2, col3 = st.columns(3)
    id = col1.text_input("Zelle ID", value=zelle["id"], max_chars=20)
    cycle = col2.number_input("Zelle Cycle", min_value=0, max_value=1000, value=zelle["Cycle"], step=1)
    qmax = col3.number_input("Zelle Cycle", min_value=0.0, max_value=30000.0, value=zelle["QMax"], step=0.1)
    info = st.text_area("Zelle Info", value=zelle["Info"], max_chars=255)
    col1, col2 = st.columns([1,3])
    if col2.button("Speichern", use_container_width= True, type="primary"):
        hash_input = f"{id}{cycle}{qmax}"
        dic = {
            "id": id,
            "Cycle": cycle,
            "QMax": qmax,
            "Info": info,
            "Art": "Manuell bearbeitet"
        }
        with st.spinner("Daten Updaten...", show_time=True):
            e = DB.update_zell(dic, zelle["hash"])
        if e is None:
            st.success(f"Zelle {id} wurde erfolgreich bearbeitet")
            st.rerun()
        else:
            st.error(f"Fehler beim Ausführen der SQL-Anfrage: {e}")
    if col1.button("Löschen", use_container_width= True, type="secondary"):
        with st.spinner("Daten Löschen", show_time=True):
            e = DB.delete_zell(zelle["hash"])
        if e is None:
            st.success(f"Zelle {id} wurde erfolgreich gelöscht")
        else:
            st.error(f"Fehler beim Ausführen der SQL-Anfrage: {e}")