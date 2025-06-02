import streamlit as st
from plotly.subplots import make_subplots
import plotly.graph_objects as go
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
            fig = make_subplots(rows=len(data.columns), cols=1, shared_xaxes=True, vertical_spacing=0.02, subplot_titles=data.columns)
            for i , col in enumerate(data.columns):
                color = combination_line[i % len(combination_line)]['color']
                #dash = combination_line[i % len(combination_line)]['line_style']
                dash = 'solid'
                fig.add_trace(go.Scatter(x=time, y=data[col], line=dict(color=color, dash=dash)),row=i+1, col=1)
                fig.update_xaxes(title_text="time_columns[0]", row=i+1, col=1)
                fig.update_yaxes(title_text=col, row=i+1, col=1)
            fig.update_layout(height=400*len(data.columns), width=1000, title_text="Zeitverlauf der Messwerte", showlegend=False, hovermode="closest")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Keine Zeitspalte gefunden.")