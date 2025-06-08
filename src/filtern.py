import streamlit as st
import pandas as pd

def zellen_filter(con):
    DB = st.session_state["DB"]
    con.subheader("Filtern")
    alle_zellen = DB.get_all_zells()
    alle_cycle = DB.get_all_cycles()
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

def daten_filer(con,data):
    alle_zellen = data["Zelle"].unique()
    zelle = con.multiselect("Zellen eingeben", alle_zellen)
    all_cycles = data["Cycle"].unique()
    all_cycles = pd.Series(all_cycles)
    all_cycles = all_cycles.sort_values().values
    cycle_sel = con.multiselect(
        "Zyklus auswählen?",
        all_cycles,
    )
    if not cycle_sel:
        cycle = all_cycles.flatten().tolist()
    else:
        cycle = cycle_sel
    return cycle, zelle