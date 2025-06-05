import streamlit as st
import plotly.express as px
import pandas as pd
from src.plotting_functions import extract_sort_keys

def Plot_Points(get_all_niquist=None):
    DB = st.session_state['DB']
    Data = DB.get_all_niquist()
    st.write(Data)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Cycles")
        selected_cycles = []
        for cycle in Plot_Data['Cycles']:
            if st.checkbox(f"Cycle {cycle}", key=f"cycle_{cycle}"):
                selected_cycles.append(cycle)

    with col2:
        st.subheader("Qcell")
        selected_socs = []
        for soc in Plot_Data['SoCs']:
            if st.checkbox(f"Qcell: {soc} mAh", key=f"Qcell_{soc}"):
                selected_socs.append(soc)

    st.divider()
    names = list(Plot_Data['Time_Plots'])
    vars = list(Plot_Data['Time_Plots'][names[0]].keys())
    if 'Plot' in vars:
        vars.remove('Plot')
    col1, col2 = st.columns(2)
    x_values = col1.selectbox("X-Axis", options=vars)
    if x_values == 'Cycle':
        selected_cycles = Plot_Data['Cycles']
    if x_values == 'QAh':
        selected_socs = Plot_Data['SoCs']
    x_log = col1.checkbox("X-Axis logarithmic?", key=f"x_log_{x_values}")
    y_values = col2.selectbox("Y-Axis", options=vars)
    y_log = col2.checkbox("Y-Axis logarithmic?", key=f"y_log_{y_values}")
    missing_selection = not selected_cycles or not selected_socs
    x_data, y_data, plot_name = [], [], []
    if st.button("Plot", type="primary", use_container_width=True, disabled=missing_selection):
        sort_plots = sorted(Plot_Data['Time_Plots'], key=extract_sort_keys)
        for Plot_Name in sort_plots:
            if Plot_Data['Time_Plots'][Plot_Name]['Cycle'] in selected_cycles and \
                    Plot_Data['Time_Plots'][Plot_Name]['QAh'] in selected_socs:
                x_data.append(Plot_Data['Time_Plots'][Plot_Name][x_values])
                y_data.append(Plot_Data['Time_Plots'][Plot_Name][y_values])
                plot_name.append(Plot_Name)
        plot_data = pd.DataFrame({x_values: x_data, y_values: y_data, "Plot": plot_name})
        fig = px.scatter(plot_data,
                         x=x_values,
                         y=y_values,
                         color="Plot",
                         title="Verläufe der EIS-Messung",
                         log_x=x_log,
                         log_y=y_log,
        )


        return fig, plot_data
