import streamlit as st
import json
import io
from app_pages.eis import Plot_EIS
from app_pages.DEIS import Plot_DEIS
from src.plotting_functions import get_linestyles

from Classes.datenbank import Database

#Run this Comand in Terminal: streamlit run /Users/janostoldy/Documents/git_projecte/ba/EIS_APP.py

DB = Database("Eis_Analyse.db","Volumes/ge95his/Datenbank")
DA = EIS_Analyse()

Data = {}
st.title("EIS App")

st.header("Analayze EIS Data")
con1 = st.container(border=True)
# Streamlit file uploader
uploaded_files = con1.file_uploader(
    "Choose a .mat file",
    accept_multiple_files=True
)
if uploaded_files:
    uploaded_files = sorted(uploaded_files, key=lambda x: x.name)
    cycle = con1.number_input("Insert a Start Cycle", min_value=0, max_value=1000, value=1, step=1)
    title = con1.text_input("Insert Export-Name", value=None, placeholder="Export Name")
    dis = not bool(title)
    if con1.button("Analyse", type="primary", use_container_width=True, disabled=dis):
        Data = (uploaded_files, cycle)

    if Data:
        con1.success("Data successfully analyzed!")
        col1, col2, col3 = con1.columns(3)
        with col1:
            st.subheader("Cycles")
            names = list(Data['Cycles'])
            st.write(names)
        with col2:
            st.subheader("Currants")
            names = list(Data['Currants'])
            st.write(names)
        with col3:
            st.subheader("SoCs")
            names = list(Data['SoCs'])
            st.write(names)

        convert_dataframes(Data)
        json_string = json.dumps(Data, indent=4)
        con1.download_button(
            label="Download Data as JSON",
            data=json_string,
            file_name=f"{title}.json",
            mime="application/json",
        )

st.header("Merge  Data")
con2 = st.container(border=True)

uploaded_files2 = con2.file_uploader(
    "Choose .json files",
    accept_multiple_files=True
)
if uploaded_files2:
    Merge = {}
    uploaded_files2 = sorted(uploaded_files2, key=lambda x: x.name)
    uploaded_files2 = [json.load(file) for file in uploaded_files2]
    title = con2.text_input("Insert Export-Name", value="Zyklus_1-53")
    dis = not bool(title)
    if con2.button("Merge", type="primary", use_container_width=True, disabled=dis):
        Merge = merge_Data(uploaded_files2)

    if Merge:
        col1, col2, col3 = con2.columns(3)
        with col1:
            st.subheader("Cycles")
            names = list(Merge['Cycles'])
            st.write(names)
        with col2:
            st.subheader("Currants")
            names = list(Merge['Currants'])
            st.write(names)
        with col3:
            st.subheader("SoCs")
            names = list(Merge['SoCs'])
            st.write(names)

        convert_dataframes(Merge)
        json_string = json.dumps(Merge, indent=4)
        con2.download_button(
            label="Download Data as JSON",
            data=json_string,
            file_name=f"{title}.json",
            mime="application/json"
        )

st.header("Plot EIS Data")
con3 = st.container(border=True)

uploaded_files3 = con3.file_uploader(
    "Choose .json files with Plot-Data",
    accept_multiple_files=False
)

if uploaded_files3:
    Plot_Data = json.load(uploaded_files3)
    convert_to_dataframes(Plot_Data)

    combination_line, combimation_dot = get_linestyles()

    options = ['EIS', 'EIS_Points','DEIS']
    col1, col2, col3 = con3.columns([2,4,1])
    selection = col2.segmented_control("", options)

    fig = None
    if selection == 'EIS':
        fig, plot_data = Plot_EIS(Plot_Data, con3)
        if fig:
            for i, trace in enumerate(fig.data):
                trace.line.color = combination_line[i % len(combination_line)]['color']  # Zyklische Farben
                trace.line.dash = combination_line[i % len(combimation_dot)]['line_style']  # Zyklische
            st.plotly_chart(fig)
            st.write(plot_data)
    elif selection == 'EIS_Points':
        fig, plot_data = Plot_EIS_Points(Plot_Data, con3)
        if fig:
            for i, trace in enumerate(fig.data):
                trace.marker.color = combimation_dot[i % len(combination_line)]['color']  # Zyklische Farben
                trace.marker.symbol = combimation_dot[i % len(combimation_dot)]['marker_type']  # Zyklische
            st.plotly_chart(fig)
            st.write(plot_data)
    elif selection == 'DEIS':
        fig, plot_data = Plot_DEIS(Plot_Data, con3)
        if fig:
            for i, trace in enumerate(fig.data):
                trace.marker.color = combimation_dot[i % len(combination_line)]['color']  # Zyklische Farben
                trace.marker.symbol = combimation_dot[i % len(combimation_dot)]['marker_type']  # Zyklische
            st.plotly_chart(fig)
            st.write(plot_data)

    if fig:
        # Weißer Hintergrund und schwarze Schrift (für Export)
        fig.update_layout(
            template="plotly",  # <- wichtig!
            paper_bgcolor='white',
            plot_bgcolor='white',
            font_color='black',
            legend_title_font_color='black',
            xaxis = dict(
                showgrid=True,
                gridcolor='#e0e0e0',  # Farbe des Grids
                gridwidth=1  # Dicke der Linien
            ),
            yaxis = dict(
                showgrid=True,
                gridcolor='#e0e0e0',
                gridwidth=1
            )
        )

        # --- Export als SVG ---
        # Temporären Buffer für SVG-Datei anlegen
        svg_buffer = io.BytesIO()
        fig.write_image(svg_buffer, format='svg', engine='kaleido', width=1200, height=800)
        svg_data = svg_buffer.getvalue()

        # Download-Button für SVG-Datei
        st.download_button(
            label="Download als SVG",
            data=svg_data,
            file_name="plot.svg",
            mime="image/svg+xml"
        )