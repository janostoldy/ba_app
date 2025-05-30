import streamlit as st
import pandas as pd
import hashlib


def zelle_app():
    st.title("Zellen")
    DB = st.session_state["DB"]
    zellen = zellen_filter(st, DB)
    zellen_hinzufuegen(st,DB)

    st.dataframe(zellen)

def zellen_hinzufuegen(st, DB):
    ex = st.expander("Zelle Hinzufügen")
    col1, col2, col3 = ex.columns(3)
    id = col1.text_input("Zelle ID", placeholder="SN0001", max_chars=10)
    cycle = col2.number_input("Zelle Cycle", min_value=0, max_value=1000, value=1, step=1)
    qmax = col3.number_input("Zelle Cycle", min_value=0.0, max_value=30000.0, value=30000.0, step=0.1)
    info = ex.text_area("Zelle Info", placeholder="Zelle Info",max_chars=255)
    if ex.button("Zelle Hinzufügen", use_container_width= True, type="primary"):
        hash_input = f"{id}{cycle}{qmax}"
        hash = hashlib.sha256(hash_input.encode()).hexdigest()
        dic = {
            "hash": hash,
            "id": id,
            "Cycle": cycle,
            "QMax": qmax,
            "Info": info
        }
        with st.spinner("Wait for it...", show_time=True):
            e = DB.insert_zell(dic)
        if e is None:
            ex.success(f"Zelle {id} erfolgreich hinzugefügt")
        else:
            ex.error(f"Fehler beim Ausführen der SQL-Anfrage: {e}")

def zelle_edit(st, DB):
    st.expander("Zelle bearbeiten")

def zellen_filter(st, DB):
    con = st.container(border=True)
    con.subheader("Zellen Filtern")
    alle_zellen = DB.query("SELECT DISTINCT id FROM Zellen")
    alle_cycle = DB.query("SELECT DISTINCT Cycle FROM Zellen")
    col1, col2 = con.columns(2)
    zellen_id = col1.selectbox("Zellen eingeben", alle_zellen,index=None,placeholder="Wähle eine Zelle aus")
    zelle_cycle = col2.selectbox("Zelle Cycle", alle_cycle,index=None,placeholder="Wähle ein Zyklus aus")

    sql = "SELECT id, Cycle, QMax, Info FROM Zellen WHERE 1=1"
    params = []

    if zellen_id is not None:
        sql += " AND id = %s"
        params.append(zellen_id)

    if zelle_cycle is not None:
        sql += " AND Cycle = %s"
        params.append(zelle_cycle)

    zellen = DB.query(sql, params=params)
    return zellen
