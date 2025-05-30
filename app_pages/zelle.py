import streamlit as st
import pandas as pd


def zelle_app():
    st.title("Zellen")
    DB = st.session_state["DB"]
    zellen_hinzufuegen(st,DB)
    zellen = zellen_filter(st,DB)

    st.dataframe(zellen)

def zellen_hinzufuegen(st, DB):
    ex = st.expander("Zelle Hinzufügen")
    col1, col2, col3 = ex.columns(3)
    id = col1.text_input("Zelle ID", placeholder="SN0001")
    cycle = col2.number_input("Zelle Cycle", min_value=0, max_value=1000, value=1, step=1)
    qmax = col3.number_input("Zelle Cycle", min_value=0.0, max_value=30000.0, value=30000.0, step=0.1)
    info = ex.text_area("Zelle Info", placeholder="Zelle Info",max_chars=255)
    if ex.button("Zelle Hinzufügen", use_container_width= True, type="primary"):
        df = pd.DataFrame([{
            "id": id,
            "Cycle": cycle,
            "QMax": qmax,
            "Info": info
        }])
        DB.insert_df(df, "Zellen")


def zellen_filter(st, DB):
    con = st.container(border=True)
    con.subheader("Zellen Filtern")
    alle_zellen = DB.query("SELECT DISTINCT id FROM Zellen")
    alle_cycle = DB.query("SELECT DISTINCT Cycle FROM Datapoints")
    col1, col2 = con.columns(2)
    zellen_id = col1.selectbox("Zellen eingeben", alle_zellen,index=None,placeholder="Wähle eine Zelle aus")
    zelle_cycle = col2.selectbox("Zelle Cycle", alle_cycle,index=None,placeholder="Wähle ein Zyklus aus")
    if zellen_id is None:
        zellen_id = alle_zellen
    if zelle_cycle is None:
        zelle_cycle = alle_cycle

    zellen = DB.query(f"SELECT * FROM Zellen WHERE id = '{zellen_id}' AND Cycle = '{zelle_cycle}'")
    return zellen
