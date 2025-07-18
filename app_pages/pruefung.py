import streamlit as st
import pandas as pd

from Classes.datenbank import Database
from src.filtern import daten_filter, soc_filer


def pruefung_app():
    st.title("Prüfungen")
    DB = Database("pruefung")
    alldata = DB.get_all_files()
    con1 = st.container(border=True)
    cyclus, zellen = daten_filter(con1, alldata)
    all_soc = DB.get_all_eis_soc()
    soc = soc_filer(con1, all_soc)

    filt_data = pd.DataFrame()
    for z in zellen:
        for cyc in cyclus:
            file = DB.get_file(cyc, z, "Kapa")
            if file.empty:
                continue
            kap = DB.get_kapa(file["name"].values[0])
            kap = pd.DataFrame(kap)
            file = DB.get_file(cyc, z, "EIS")
            if file.empty:
                continue
            if not isinstance(file, list):
                file = [file]
            for f in file:
                for s in soc:
                    points = DB.get_eis_points(f["name"].values[0],s)
                    points = pd.DataFrame(points)
                    if points.empty:
                        continue
                    zif = points["freq_zif"]
                    dat = pd.DataFrame({
                        "Zelle": z,
                        "Zyklus": cyc,
                        "SoC": s,
                        "Datum": f["datum"],
                        "Kap": kap["kapa"].values[0],
                        "ZIF": zif,
                        "RE_ZIF": points["re_zif"]
                    })
                    filt_data = pd.concat([filt_data, dat], ignore_index=True)

    st.dataframe(filt_data)