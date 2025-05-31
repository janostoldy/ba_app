import streamlit as st
import plotly.express as px
from galvani import BioLogic
import pandas as pd
from config import mes_spalten
from src.plotting_functions import Get_Colors

def analyse_app():
    st.title("Daten Analysieren")
    con1 = st.container(border=True)
    uploaded_file = con1.file_uploader("Datei Auswählen", type=["mpr","csv"])
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.mpr'):
            mpr_file = BioLogic.MPRfile(uploaded_file)
            df = pd.DataFrame(mpr_file.data)
            df = df.rename(columns=mes_spalten)
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)

    if 'df' in locals():
        st.dataframe(df)
        combination_line, combination_dot = Get_Colors()
        time_columns = [col for col in df.columns if 'time' in col.lower()]
        if time_columns:
            time = df[time_columns[0]]
            data = df.drop(time_columns[0], axis=1)
            for i , col in enumerate(data.columns):
                color = combination_line[i % len(combination_line)]['color']
                #dash = combination_line[i % len(combination_line)]['line_style']
                dash = 'solid'
                fig = px.line(x=time, y=data[col], labels={'x': time_columns[0], 'y': col}, title=f"{col}")
                fig.update_traces(line=dict(color=color, dash=dash))
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Keine Zeitspalte gefunden.")