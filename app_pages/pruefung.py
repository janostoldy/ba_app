import streamlit as st
import pandas as pd
from src.filtern import daten_filter, soc_filer


def pruefung_app():
    st.title("Prüfungen")
    DB = st.session_state["DB"]
    alldata = DB.get_all_files()
    con1 = st.container(border=True)
    cyclus, zellen = daten_filter(con1, alldata)
    all_soc = DB.get_all_eis_soc()
    soc = soc_filer(con1, all_soc)

    filt_data = pd.DataFrame()
    for z in zellen:
        for cyc in cyclus:
            for s in soc:
                file = DB.get_file(cyc, z,"Kapa")
                kap = DB.get_kapa(file["name"].values[0])
                file = DB.get_file(cyc, z,"EIS")
                points = DB.get_eis_points(file["name"].values[0],s)
                zif = points["freq_ZIF"]
                dat = pd.DataFrame({
                    "Zelle": z,
                    "Zyklus": cyc,
                    "SoC": s,
                    "Datum": file["Datum"],
                    "Kap": kap["Kapa"].values[0],
                    "ZIF": zif,
                    "RE_ZIF": points["Re_ZIF"]
                })
                filt_data = pd.concat([filt_data, dat], ignore_index=True)

    st.dataframe(filt_data)