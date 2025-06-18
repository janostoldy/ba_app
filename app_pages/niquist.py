import streamlit as st
import plotly.express as px
import pandas as pd
import io
from src.filtern import daten_filter, soc_filer
from src.plotting_functions import colors

def points_app():
    st.title("Points")
    DB = st.session_state["DB"]
    alldata = DB.get_all_eis()
    con1 = st.container(border=True)
    cycle, zelle = daten_filter(con1, alldata)
    all_soc = DB.get_all_eis_soc()
    soc = soc_filer(con1, all_soc)
    filt_data = pd.DataFrame()
    spalten = ["Datei", "SoC", "Zelle", "Cycle", "Datum"]
    if not cycle or not zelle:
        st.warning("Keine Werte ausgewählt")
    else:
        con1 = st.container(border=False)
        data = pd.DataFrame()
        for z in zelle:
            for c in cycle:
                for s in soc:
                    file = DB.get_file(c, z, "EIS")
                    cycle_data = DB.get_eis_points(file["name"].values[0],s)
                    filt_data = pd.concat([filt_data, cycle_data[spalten]])
                    data = pd.concat([data, cycle_data])

        con1.subheader("Ausgewählte Daten:")
        con1.write(filt_data)
        con1.subheader("Plots:")

        key = 0
        col1, col2 = con1.columns(2)
        options = ["SoC", "Zelle"]
        selected = col1.segmented_control("Subplots",options,help="Wähle Wert aus der in einem Diagramm angezeigt wird",default=options[1])
        if selected == "SoC":
            plots = soc
            plot_name = "SoC"
            subplots = "Zelle"
            einheit = "mAh"
        else:
            plots = zelle
            plot_name = "Zelle"
            subplots = "SoC"
            einheit = ""

        options = [col for col in data.columns if col not in ["Datei", "Cycle", "Zelle", "Datum", "SoC"]]
        y_values = col2.selectbox("Y-Werte", options)

        for p in plots:
            con2 = st.container(border=False)
            con2.divider()
            data_mod = data[data[plot_name] == p]
            name = f"{plot_name} {p} {einheit}"
            fig = plot_points(data_mod, name, y_values,subplots)
            con2.plotly_chart(fig)
            fig.update_layout(
                template="plotly",  # <- wichtig!
                paper_bgcolor='white',
                plot_bgcolor='white',
                font_color='black',
                legend_title_font_color='black',
                xaxis=dict(
                    showgrid=True,
                    gridcolor='#e0e0e0',  # Farbe des Grids
                    gridwidth=1  # Dicke der Linien
                ),
                yaxis=dict(
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
            space, col2 = con2.columns([4, 1])
            col2.download_button(
                label="Download als SVG",
                data=svg_data,
                file_name="plot.svg",
                mime="image/svg+xml",
                key=key,
                use_container_width=True
            )
            key += 1

            con2.dataframe(data_mod)

def niqhist_app():
    st.write("Niqhist")
    DB = st.session_state["DB"]
    alldata = DB.get_all_eis()
    con1 = st.container(border=True)
    cycle, zelle = daten_filter(con1, alldata)
    all_soc = DB.get_all_eis_soc()
    soc = soc_filer(con1, all_soc)
    filt_data = pd.DataFrame()
    spalten = ["Datei", "SoC", "Zelle", "Cycle", "Datum"]
    if not cycle or not zelle:
        st.warning("Keine Werte ausgewählt")
    else:
        con1 = st.container(border=False)
        data = pd.DataFrame()
        for z in zelle:
            for c in cycle:
                for s in soc:
                    file = DB.get_file(c, z, "EIS")
                    cycle_data = DB.get_eis_plots(file["name"].values[0], s)
                    filt_data = pd.concat([filt_data, cycle_data[spalten]])
                    data = pd.concat([data, cycle_data])

        con1.subheader("Ausgewählte Daten:")
        con1.write(filt_data)
        con1.subheader("Plots:")

def plot_points(data, name, y_values, subplots):
    fig = px.line(data,
                  x="Cycle",
                  y=y_values,
                  color=subplots,
                  title=f"{y_values} von {name}",
                  markers=True,
                  color_discrete_sequence=list(colors.values())
                  )
    fig.update_layout(
        yaxis_title=y_values,
        xaxis_title='Zyklken',
        template='simple_white',
    )
    return fig