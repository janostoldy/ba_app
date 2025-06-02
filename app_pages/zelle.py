import streamlit as st
import hashlib

from streamlit import session_state


def zelle_app():
    st.title("Zellen")
    zellen_filter()

    col1, col2 = st.columns(2)
    if col1.button("Daten oder Zelle hinzufügen", use_container_width= True, type="primary"):
        zellen_hinzufuegen()
    if col2.button("Daten bearbeiten", use_container_width= True, type="secondary"):
        zelle_edit()
    st.divider()

    DB = st.session_state["DB"]
    zellen = DB.get_zellen(st.session_state["zelle_filter"]["zellen_id"],st.session_state["zelle_filter"]["zellen_cycle"])
    st.dataframe(zellen[["id", "Cycle", "QMax", "Info"]])

@st.dialog("Neue Daten einer Zelle Hinzufügen",width="large")
def zellen_hinzufuegen():
    col1, col2, col3 = st.columns(3)
    id = col1.text_input("Zelle ID", placeholder="SN0001", max_chars=20)
    cycle = col2.number_input("Zelle Cycle", min_value=0, max_value=1000, value=1, step=1)
    qmax = col3.number_input("Zelle Cycle", min_value=0.0, max_value=30000.0, value=0.0, step=0.1)
    info = st.text_area("Zelle Info", placeholder="Zelle Info",max_chars=255)
    if st.button("Daten Hinzufügen", use_container_width= True, type="primary"):
        hash_input = f"{id}{cycle}{qmax}"
        hash = hashlib.sha256(hash_input.encode()).hexdigest()
        dic = {
            "hash": hash,
            "id": id,
            "Cycle": cycle,
            "QMax": qmax,
            "Info": info
        }
        with st.spinner("Daten hinzufügen...", show_time=True):
            DB = st.session_state["DB"]
            e = DB.insert_zell(dic)
        if e is None:
            st.success(f"Zelle {id} erfolgreich hinzugefügt")
            st.rerun()
        else:
            st.error(f"Fehler beim Ausführen der SQL-Anfrage: {e}")

@st.dialog("Daten Bearbeiten",width="large")
def zelle_edit():
    st.write("Index der Zelle aus dem Dargestellten Dataframe:")
    DB = st.session_state["DB"]
    zellen_id = st.session_state["zelle_filter"]["zellen_id"]
    zellen_cycle= st.session_state["zelle_filter"]["zellen_cycle"]
    zellen = DB.get_zellen(zellen_id,zellen_cycle)
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
        hash = hashlib.sha256(hash_input.encode()).hexdigest()
        dic = {
            "hash": hash,
            "id": id,
            "Cycle": cycle,
            "QMax": qmax,
            "Info": info
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
            st.rerun()
        else:
            st.error(f"Fehler beim Ausführen der SQL-Anfrage: {e}")

def zellen_filter():
    DB = st.session_state["DB"]
    con = st.container(border=True)
    con.subheader("Zellen Filtern")
    alle_zellen = DB.query("SELECT DISTINCT id FROM Zellen")
    alle_cycle = DB.query("SELECT DISTINCT Cycle FROM Zellen")
    col1, col2 = con.columns(2)

    if "zelle_filter" not in st.session_state:
        st.session_state["zelle_filter"] = {
            "zellen_id": None,
            "zellen_cycle": None
        }

    zellen_id = col1.selectbox("Zellen eingeben", alle_zellen,index=None,placeholder="Wähle eine Zelle aus")
    zelle_cycle = col2.selectbox("Zelle Cycle", alle_cycle,index=None,placeholder="Wähle ein Zyklus aus")

    st.session_state["zelle_filter"] = {
        "zellen_id": zellen_id,
        "zellen_cycle": zelle_cycle
    }
