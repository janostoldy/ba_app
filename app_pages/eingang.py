import streamlit as st
import pandas as pd
from src.filtern import zellen_filter

def eingang_app():
    st.title("Eingangsprüfung")
    DB = st.session_state["DB"]
    alldata = DB.get_all_eingang()
    zellen = alldata["Zelle"].unique()

    filt_data = pd.DataFrame()
    for z in zellen:
        file = DB.get_file(0, z,"Kapa")
        kap = DB.get_kapa(file["name"].values[0])
        dat = pd.DataFrame({
            "Zelle": z,
            "Datum": file["Datum"],
            "Kap": kap["Kapa"].values[0],
            "ZIF": ""
        })
        filt_data = pd.concat([filt_data, dat], ignore_index=True)

    st.dataframe(filt_data)