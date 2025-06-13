import streamlit as st
import pandas as pd

def kapa_filter(con):
    DB = st.session_state["DB"]
    con.subheader("Filtern")
    alle_zellen = DB.get_all_zells()
    alle_cycle = DB.get_kapa_cycles()
    col1, col2 = con.columns(2)

    zellen_id = col1.multiselect("Zellen eingeben", alle_zellen,placeholder="Wähle eine Zelle aus")
    zelle_cycle = col2.multiselect("Zelle Cycle", alle_cycle,placeholder="Wähle ein Zyklus aus")

    return zellen_id, zelle_cycle

def daten_filer(con,data):
    con.subheader("Filter")
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