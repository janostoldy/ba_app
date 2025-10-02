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
    data_df = df[df["freqhz"].between(195, 205)]
    data_df = data_df[data_df["calc_ima"]==0]

    fig = px.scatter_3d(data_df,
                        x='soc',
                        y='temperaturec',
                        z='phasezdeg',
                        hover_data=["datei"]
                        )
    st.plotly_chart(fig)