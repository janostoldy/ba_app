import plotly.express as px
import streamlit as st
import pandas as pd
from classes.datenbank import Database

def lup_app():
    with st.sidebar:
        side = st.radio(
            "Wähle eine Option",
            ("Table", "Formierung", "Fit")
        )
    if side == "Table":
        table_app()
    elif side == "Formierung":
        form_app()
    else:
        fit_app()

def table_app():
    st.title("Creat Look-Up-Table")
    DB = Database("lup")
    df = DB.get_lup()
    df['calc_soc'] = df['soc']/2500 + 0.1
    plots = ['phasezdeg', 'calc_rezohm', 'calc_imzohm']

    data_df = df[df["calc_ima"]==1250]
    data_df = data_df[data_df["freqhz"].between(195, 205)]
    data_df["temperaturec_cat"] = data_df["temperaturec"].astype(str)
    data_df = data_df.sort_values("soc")
    for plot in plots:
        st.subheader(plot + ' 200 Hz')
        fig = px.scatter(data_df,
                        x='calc_soc',
                        y=plot,
                        color='temperaturec_cat',
                        hover_data=["datei"],
                        symbol="temperaturec_cat",
                         )
        st.plotly_chart(fig)

def form_app():
    st.title("Formierungs Data")
    DB = Database("lup")
    df = DB.get_deis()
    st.write(df)
    df['calc_soc'] = df['soc']/2500
    plots = ['phasezdeg', 'calc_rezohm', 'calc_imzohm']

    data_df = df[df["calc_ima"]==0]
    data_df = data_df.sort_values(["soc","cycle"])
    for plot in plots:
        st.subheader(plot + ' 200 Hz')
        fig = px.line(data_df,
                        x='calc_soc',
                        y=plot,
                        color='cycle',
                        )
        st.plotly_chart(fig)

    socs = [0.2,0.5,0.8]
    data_df = df[df["calc_ima"]==0]
    data_df = data_df[data_df["calc_soc"].isin(socs)]
    data_df = data_df.sort_values(["soc","cycle"])
    for plot in plots:
        st.subheader(plot + ' 200 Hz')
        fig = px.line(data_df,
                        x='cycle',
                        y=plot,
                        color='calc_soc',
                        )
    st.plotly_chart(fig)