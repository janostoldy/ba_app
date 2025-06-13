import pandas as pd
import streamlit as st
import pandas as pd
from src.filtern import kapa_filter

def kapazität_app():
    st.title("Kapazität")
    DB = st.session_state["DB"]
    alldata = DB.get_all_kapa()
    con1 = st.container(border=True)
    zelle, cycle = kapa_filter(con1)
    filt_data = alldata.iloc[0:0].copy()
    if not cycle or not zelle:
        st.warning("Keine Werte ausgewählt")
    else:
        con1 = st.container(border=False)

        for z in zelle:
            for c in cycle:
                con2 = st.container(border=False)
                con2.divider()
        con1.subheader("Ausgewählte Daten:")
        con1.write(filt_data)
        con1.subheader("Plots:")


def plot_kapa():
    st.write("test")
