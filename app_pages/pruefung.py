import streamlit as st
import pandas as pd
from src.filtern import zellen_filter, daten_filter


def pruefung_app():
    st.title("Prüfungen")
    DB = st.session_state["DB"]
    alldata = DB.get_all_files()
    con1 = st.container(border=True)
    cyclus, zellen = daten_filter(con1, alldata)

    filt_data = pd.DataFrame()
    for z in zellen:
        for cyc in cyclus:
            file = DB.get_file(cyc, z,"Kapa")
            kap = DB.get_kapa(file["name"].values[0])
            dat = pd.DataFrame({
                "Zelle": z,
                "Zyklus": cyc,
                "Datum": file["Datum"],
                "Kap": kap["Kapa"].values[0],
                "ZIF": ""
            })
            filt_data = pd.concat([filt_data, dat], ignore_index=True)

    st.dataframe(filt_data)