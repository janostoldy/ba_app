import streamlit as st
import plotly.express as px
import pandas as pd
from classes.datenanalyse import Analyse
from classes.datenbank import Database
from src.filtern import daten_filter, soc_filer
from src.plotting_functions import colors, download_button

def eis_app():
    with st.sidebar:
        side = st.radio(
            "Wähle eine Option",
            ("Kurven", "Punkte")
        )
    if side == "Kurven":
        niqhist_app()
    else:
        points_app()

def points_app():
    st.title("Points")
    DB = Database("Points")
    alldata = DB.get_all_eis()
    con1 = st.container(border=True)
    cycle, zelle = daten_filter(con1, alldata)
    all_soc = DB.get_all_eis_soc()
    soc = soc_filer(con1, all_soc)
    filt_data = pd.DataFrame()
    spalten = ["datei", "soc", "zelle", "cycle", "datum"]
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
                    cycle_data = pd.DataFrame(cycle_data)
                    if cycle_data.empty:
                        continue
                    filt_data = pd.concat([filt_data, cycle_data[spalten]])
                    data = pd.concat([data, cycle_data])

        con1.subheader("Ausgewählte Daten:")
        con1.write(filt_data)
        con1.subheader("Plots:")

        key = 0
        col1, col2 = con1.columns(2)
        options = ["SoC", "Zelle", "Zyklus"]
        selected = col1.segmented_control("Subplots",options,help="Wähle Wert aus der in einem Diagramm angezeigt wird",default=options[1])
        options = [col for col in data.columns if col not in ["datei", "cycle", "zelle", "datum", "soc"]]
        y_values = col2.selectbox("Y-Werte", options)
        graphs = col2.toggle("Alle Grafen in einem Plot")
        zero = col2.toggle("Startpunkt normalisieren")
        if not graphs:
            if selected == "SoC":
                plots = soc
                plot_name = "soc"
                subplots = "zelle"
                einheit = "mAh"
                x_values = "cycle"
            elif selected == "Zyklus":
                plots = zelle
                plot_name = "zelle"
                subplots = "cycle"
                x_values = "soc"
                einheit = "mAh"
            else:
                plots = zelle
                plot_name = "zelle"
                subplots = "soc"
                x_values = "cycle"
                einheit = ""
        else:
            plots = ["allen ausgewählten Daten"]
            plot_name = ""
            data_mod = data
            subplots = "zelle"
            x_values = "cycle"
            einheit = ""

        for p in plots:
            con2 = st.container(border=False)
            con2.divider()
            if not graphs:
                data_mod = data[data[plot_name] == p]
            if selected == "Zyklus":
                data_mod.sort_values("soc", inplace=True)
            name = f"{plot_name} {p} {einheit}"
            fig = plot_points(data_mod, name, x_values, y_values,subplots)
            con2.plotly_chart(fig)
            space, col2 = con2.columns([4, 1])
            download_button(col2,fig,key)
            key += 1

            con2.dataframe(data_mod)

def niqhist_app():
    st.title("EIS")
    DB = Database("EIS")
    alldata = DB.get_all_eis()
    con1 = st.container(border=True)
    cycle, zelle = daten_filter(con1, alldata)
    all_soc = DB.get_all_eis_soc()
    soc = soc_filer(con1, all_soc)
    filt_data = pd.DataFrame()
    spalten = ["datei", "soc", "zelle", "cycle", "datum"]
    if not cycle or not zelle:
        st.warning("Keine Werte ausgewählt")
    else:
        con1 = st.container(border=False)
        data = pd.DataFrame()
        data_list = []
        for z in zelle:
            for c in cycle:
                file = DB.get_file(c, z, "EIS")
                if file.empty:
                    continue
                for s in soc:
                    cycle_data = DB.get_eis_plots(file["name"].values[0], s)
                    cycle_data = pd.DataFrame(cycle_data)
                    if cycle_data.empty:
                        continue
                    filt_data = pd.concat([filt_data, cycle_data[spalten]])
                    data = pd.concat([data, cycle_data])
                    data_list.append(cycle_data)


        con1.subheader("Ausgewählte Daten:")
        con1.write(filt_data.drop_duplicates())
        if con1.button("Daten Aktualisieren", type="secondary", use_container_width=True,
                       help="Führt die Niqhist-Analyse ein weiteres mal durch um neue Datenpunkte hinzuzufügen"):
            DA = Analyse()
            DA.calc_niquist_data(data_list,True)
        con1.subheader("Plots:")

        key = 0
        col1, col2 = con1.columns(2)

        kHz = col2.toggle("2kHz anzeigen")
        tabels = col2.toggle("Tabellen anzeigen")
        graphs = col2.toggle("Alle Grafen in einem Plot")
        options = ["soc", "cycle","zelle"]
        big_plot = col1.segmented_control("Daten", options,
                                          help="Wähle Wert der einzelnen Diagramme",
                                          default=options[2],
                                          disabled=graphs)
        options = ["Niqhist", "Bode-Re", "Bode-Im", "Bode-Phase"]
        plot = col1.segmented_control("Plots",options,default=options[0])
        if plot == "Niqhist":
            x_data = "calc_rezohm"
            y_data = "calc_imzohm"
            log_x = False
        elif plot == "Bode-Re":
            x_data = "freqhz"
            y_data = "calc_rezohm"
            log_x = True
        elif plot == "Bode-Im":
            x_data = "freqhz"
            y_data = "calc_imzohm"
            log_x = True
        elif plot == "Bode-Phase":
            x_data = "freqhz"
            y_data = "phasezdeg"
            log_x = True

        if not graphs:
            if big_plot == "soc":
                plots = soc
                plot_name = "soc"
            elif big_plot == "cycle":
                plots = cycle
                plot_name = "cycle"
            elif big_plot == "zelle":
                plots = zelle
                plot_name = "zelle"

        else:
            plots = ["allen ausgewählten Daten"]
            data_mod = data
            plot_name = ""

        subplots = 'color'

        for p in plots:
            con2 = st.container(border=False)
            con2.divider()
            if not graphs:
                data_mod = data[data[plot_name] == p]
                if data_mod.empty:
                    continue
            data_mod['color'] = data_mod['zelle'].astype(str) + "_" + data_mod['cycle'].astype(str) + "_" + data_mod['soc'].astype(str)
            data_mod.sort_values(by=["datei","freqhz"], inplace=True)

            if not kHz:
                data_mod = data_mod[data_mod["freqhz"] != 1999]
            name = f"Niqhist plot von {p}"
            fig = plot_graphs(data_mod, name,subplots,x_data,y_data, log_x)
            con2.plotly_chart(fig)
            space, col2 = con2.columns([4, 1])
            download_button(col2,fig,key)
            key += 1
            if tabels:
                con2.dataframe(data_mod)

def plot_points(data, name,x_values, y_values, subplots):
    fig = px.line(data,
                  x=x_values,
                  y=y_values,
                  color=subplots,
                  title=f"{y_values} von {name}",
                  markers=True,
                  color_discrete_sequence=list(colors.values()),
                  )
    fig.update_layout(
        yaxis_title=y_values,
        xaxis_title=x_values,
        template='simple_white',
    )
    return fig

def plot_graphs(data, name, subplots, x, y, log):
    fig = px.line(data,
                  x=x,
                  y=y,
                  color=subplots,
                  log_x = True,
                  title=name,
                  markers=True,
                  color_discrete_sequence=list(colors.values()),
                  hover_data="freqhz"
                  )

    return fig