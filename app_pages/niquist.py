import streamlit as st
import plotly.express as px
import pandas as pd
from Classes.datenanalyse import Analyse
from src.filtern import daten_filter, soc_filer
from src.plotting_functions import colors, download_button

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
                file = DB.get_file(c, z, "EIS")
                if file.empty:
                    continue
                for s in soc:
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
        options = [col for col in data.columns if col not in ["Datei", "Cycle", "Zelle", "Datum", "SoC"]]
        y_values = col2.selectbox("Y-Werte", options)
        graphs = col2.toggle("Alle Grafen in einem Plot")
        if not graphs:
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
        else:
            plots = ["allen ausgewählten Daten"]
            plot_name = ""
            data_mod = data
            subplots = "Zelle"
            einheit = ""

        for p in plots:
            con2 = st.container(border=False)
            con2.divider()
            if not graphs:
                data_mod = data[data[plot_name] == p]
            name = f"{plot_name} {p} {einheit}"
            fig = plot_points(data_mod, name, y_values,subplots)
            con2.plotly_chart(fig)
            space, col2 = con2.columns([4, 1])
            download_button(col2,fig,key)
            key += 1

            con2.dataframe(data_mod)

def niqhist_app():
    st.title("Niqhist")
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
        data_list = []
        for z in zelle:
            for c in cycle:
                for s in soc:
                    file = DB.get_file(c, z, "EIS")
                    if file.empty:
                        continue
                    cycle_data = DB.get_eis_plots(file["name"].values[0], s)
                    filt_data = pd.concat([filt_data, cycle_data[spalten]])
                    data = pd.concat([data, cycle_data])
                    data_list.append(cycle_data)
        data.drop(columns=["hash"], inplace=True)

        con1.subheader("Ausgewählte Daten:")
        con1.write(filt_data.drop_duplicates())
        if con1.button("Daten Aktualisieren", type="secondary", use_container_width=True,
                       help="Führt die Niqhist-Analyse ein weiteres mal durch um neue Datenpunkte hinzuzufügen"):
            DA = Analyse(DB)
            DA.calc_niquist_data(data_list,True)
        con1.subheader("Plots:")

        key = 0
        col1, col2 = con1.columns(2)
        options = ["SoC", "Zyklus"]

        kHz = col2.toggle("2kHz anzeigen")
        tabels = col2.toggle("Tabellen anzeigen")
        graphs = col2.toggle("Alle Grafen in einem Plot")

        selected = col1.segmented_control("Subplots", options,
                                          help="Wähle Wert aus der in einem Diagramm angezeigt wird",
                                          default=options[1],
                                          disabled=graphs)

        if not graphs:
            if selected == "SoC":
                plots = zelle
                plot_name = "Zelle"
                subplots = "SoC"
                subplot_name = "über SoC"
            else:
                plots = zelle
                plot_name = "Zelle"
                subplots = "Cycle"
                subplot_name = "über Zyklus"
        else:
            plots = ["allen ausgewählten Daten"]
            data_mod = data
            plot_name = ""
            subplot_name = ""
            subplots  = "Datei"


        for p in plots:
            con2 = st.container(border=False)
            con2.divider()
            if not graphs:
                data_mod = data[data[plot_name] == p]
            data_mod.sort_values(by=["Datei","freqHz"], inplace=True)

            if not kHz:
                data_mod = data_mod[data_mod["freqHz"] != 1999]
            name = f"Niqhist plot von {p} {subplot_name}"
            fig = plot_graphs(data_mod, name,subplots)
            con2.plotly_chart(fig)
            space, col2 = con2.columns([4, 1])
            download_button(col2,fig,key)
            key += 1
            if tabels:
                con2.dataframe(data_mod)

def plot_points(data, name, y_values, subplots):
    fig = px.line(data,
                  x="Cycle",
                  y=y_values,
                  color=subplots,
                  title=f"{y_values} von {name}",
                  markers=True,
                  color_discrete_sequence=list(colors.values()),
                  )
    fig.update_layout(
        yaxis_title=y_values,
        xaxis_title='Zyklken',
        template='simple_white',
    )
    return fig

def plot_graphs(data, name, subplots):
    fig = px.line(data,
                  x="calc_ReZOhm",
                  y="calc_ImZOhm",
                  color=subplots,
                  title=name,
                  markers=True,
                  color_discrete_sequence=list(colors.values()),
                  hover_data="freqHz"
                  )
    fig.update_layout(
        yaxis_title='ImZ (Ohm)',
        xaxis_title='ReZ (Ohm)',
        template='simple_white',
    )
    return fig