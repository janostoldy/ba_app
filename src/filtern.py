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

def daten_filter(con, data):
    con.subheader("Filter")
    zelle = zellen_filter(con, data)
    all_cycles = data["cycle"].unique()
    all_cycles = pd.Series(all_cycles)
    all_cycles = all_cycles.sort_values().values
    cycle_sel = con.multiselect(
        "Zyklus auswählen?",
        all_cycles,
        placeholder="Alle Zyklen ausgewählt"
    )
    if not cycle_sel:
        cycle = all_cycles.flatten().tolist()
    else:
        cycle = cycle_sel
    return cycle, zelle

def zellen_filter(con,data):
    alle_zellen = data["zelle"].unique()
    zelle_sel = con.multiselect(
        "Zellen eingeben",
        alle_zellen,
        placeholder="Alle Zellen ausgewählt"
    )
    if not zelle_sel:
        zelle = alle_zellen.flatten().tolist()
    else:
        zelle = zelle_sel
    return zelle

def typ_filer(con,data):
    alle_typ = data["Typ"].unique()
    typ_sel = con.multiselect(
        "Typ",
        alle_typ,
        placeholder="Alle Typen ausgewählt"
    )
    if not typ_sel:
        typ = alle_typ.flatten().tolist()
    else:
        typ = typ_sel
    return typ

def soc_filer(con,data):
    alle_soc = data["soc"].unique()
    soc_sel = con.multiselect(
        "SoC",
        alle_soc,
        placeholder="Alle Typen ausgewählt"
    )
    if not soc_sel:
        typ = alle_soc.flatten().tolist()
    else:
        typ = soc_sel
    return typ