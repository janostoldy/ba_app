import plotly.express as px
import streamlit as st
import pandas as pd
import numpy as np
from classes.datenbank import Database
from src.ecb_model import model

# von dort aus zur SVG navigieren
def ecd_app():
    st.title("ECD-Analyse")
    DB = Database("ECD")
    bio = DB.get_imp_bio()
    bio = bio[bio["freq"] <= 1900]
    data_df = pd.DataFrame({
        'Re': bio["re"],
        'Im': bio["im"],
        'freq': bio["freq"],
        'typ': 'biologic'
    })
    # --- Anregung ---
    #st.subheader("Frequenzen:")
    #with st.expander("Erweitern"):
    #freq = pd.DataFrame([5, 10, 15, 20, 25, 35, 55, 80, 120, 180, 270, 405, 605, 900, 1340, 2000])
    #edit_freq = st.data_editor(freq.T)
    #frequencies = edit_freq.values.flatten().tolist()
    #col1, col2 = st.columns(2)
    #i_offset = col1.number_input("i_offset")
    #i_anregung = col2.number_input("i_anregung")

    # --- Signal generieren ---
    #signals = []
    #time_abs = 0
    #for f in frequencies[::-1]:
    #    time = 1 /f
    #    time_abs += time
    #    t = np.linspace(0, time, int(200000 / f))
    #    sig = i_offset + i_anregung * np.sin(2 * np.pi * f * t)
    #    signals.append(sig)

    #full_signal = np.concatenate(signals)
    #full_time = np.linspace(0, time_abs, len(full_signal))
    #fig = px.line(x=full_time ,y=full_signal)
    #st.plotly_chart(fig)

    st.subheader("Parameter eingeben:")

    con1 = st.container(border=True)
    con1.image("src/pic/ecb_lib.png", use_container_width=True)
    sec = con1.toggle("Zweiter RC-Glied")
    col1, col2, col3, col4 = con1.columns([2,2,3,3])
    # --- Parameter ---
    x = np.zeros(8)
    x[0] = col1.number_input("L",value=0.43,step=0.01)
    x[1] = col2.number_input("R_s / milliOhm",value=22.5,step=0.1)
    x[3] = col3.number_input("C_SEI",value=0.15,step=0.1)
    #x[6] = col3.number_input("alpha_SEI",value=0.8,step=0.1)
    x[6] = 1
    x[2] = col3.number_input("R_SEI / milliOhm",value=4.7,step=0.1)
    if sec:
        x[5] = col4.number_input("C_dl",value=0.9,step=0.1)
        #x[7] = col4.number_input("alpha_ct",value=0.8,step=0.1)
        x[7] = 1
        x[4] = col4.number_input("R_ct",value=5.4,step=0.1)
    else:
        x[5] = 1
        x[7] = 1
        x[4] = 1
    frequencies = np.logspace(np.log10(5), np.log10(1600), num=26)
    frequencies = np.array(frequencies, dtype=float)
    st.subheader("Berechnung:")
    Re, Im = model(x,frequencies, sec)
    st.subheader("Beschreibung:")
    data = pd.concat([data_df, pd.DataFrame({
        'Re': Re,
        'Im': Im,
        'freq': frequencies,
        'typ': 'calc'
    })])
    fig = px.line(data,
                  x='Re',
                  y='Im',
                  color='typ',
                  hover_data='freq',
                  )
    st.plotly_chart(fig)
    fig = px.line(data,
                  x='freq',
                  y='Re',
                  log_x=True,
                  color='typ',
                  )
    st.plotly_chart(fig)
    fig = px.line(data,
                  x='freq',
                  y='Im',
                  log_x=True,
                  color='typ',
                  )
    st.plotly_chart(fig)



