import streamlit as st
from streamlit import session_state
import plotly.express as px
import pandas as pd

from Classes.datenbank import Database
from src.filtern import daten_filter
from src.plotting_functions import extract_sort_keys
from src.db_help import check_db

def eis_app():
    st.title("EIS Analyse")
    DB = Database("EIS")
    con1 = st.container(border=True)
    data = DB.get_all_eis()
    cycle, zelle = daten_filter(con1, data)

def Plot_EIS():
    DB = Database("EIS")
    all_cycles = DB.query("SELECT DISTINCT Cycle FROM EIS")
    all_socs = DB.query("SELECT DISTINCT ROUND(QQomAh / 25.0) * 25 AS QQomAh FROM EIS")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Cycles")
        selected_cycles = []
        for cycle in all_cycles:
            if st.checkbox(f"Cycle {cycle[0]}", key=f"cycle_{cycle[0]}"):
                selected_cycles.append(cycle)

    with col2:
        st.subheader("Qcell")
        selected_socs = []
        for soc in all_socs:
            if st.checkbox(f"Qcell: {soc[0]} mAh", key=f"Qcell_{soc[0]}"):
                selected_socs.append(soc)
    st.divider()
    names = list(Plot_Data['Time_Plots'])
    vars = Plot_Data['Time_Plots'][names[0]]['Plot'].keys()
    col1, col2 = st.columns(2)
    x_values = col1.selectbox("X-Axis", options=vars)
    x_log = col1.checkbox("X-Axis logarithmic?", key=f"x_log_{x_values}")
    y_values = col2.selectbox("Y-Axis", options=vars)
    y_log = col2.checkbox("Y-Axis logarithmic?", key=f"y_log_{y_values}")
    plot_data = pd.DataFrame()
    missing_selection = not selected_cycles or not selected_socs
    if st.button("Plot", type="primary", use_container_width=True, disabled=missing_selection):
        sort_plots = sorted(Plot_Data['Time_Plots'], key=extract_sort_keys)
        for Plot in sort_plots:
            if Plot_Data['Time_Plots'][Plot]['Cycle'] in selected_cycles and \
                    Plot_Data['Time_Plots'][Plot]['QAh'] in selected_socs:
                x_data = Plot_Data['Time_Plots'][Plot]['Plot'][x_values]
                y_data = Plot_Data['Time_Plots'][Plot]['Plot'][y_values]
                df_temp = pd.DataFrame({x_values: x_data, y_values: y_data, "Plot": Plot})
                plot_data = pd.concat([plot_data, df_temp], ignore_index=True)
        fig = px.line(plot_data, x=x_values, y=y_values, color="Plot", title="Verläufe der EIS-Messung", log_x=x_log, log_y=y_log)
        return fig, plot_data
    else:
        return None, None