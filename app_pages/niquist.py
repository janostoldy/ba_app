import streamlit as st
import plotly.express as px
import pandas as pd
from src.auswertung import rel_dev_to_median
from classes.datenanalyse import Analyse
from classes.datenbank import Database
from src.filtern import daten_filter, soc_filer
from src.plotting_functions import colors, download_button

def eis_app():
    with st.sidebar:
        side = st.radio(
            "Wähle eine Option",
            ("Kurven", "Punkte", "Formierung")
        )
    if side == "Kurven":
        niqhist_app()
    elif side == "Punkte":
        points_app()
    else:
        form_app()

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
        options = ["cycle","cap_cycle","soc"]
        x_values = col1.segmented_control("X-Achse", options,default=options[0])
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
            elif selected == "Zyklus":
                plots = zelle
                plot_name = "zelle"
                subplots = "cycle"
                einheit = "mAh"
            else:
                plots = zelle
                plot_name = "zelle"
                subplots = "soc"
                einheit = ""
        else:
            plots = ["allen ausgewählten Daten"]
            plot_name = ""
            data_mod = data
            subplots = "zelle"
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
        options = ["Niqhist", "Bode-Re", "Bode-Im", "Bode-Phase","Bode-Z"]
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
        elif plot == "Bode-Z":
            x_data = "freqhz"
            y_data = "zohm"
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

def form_app():
    st.title("Formierungs Analyse")
    DB = Database("form")
    data = DB.get_form()
    st.write(data)
    if st.button("Werte Berechnen", type="primary") or True:
        #eis = DB.get_all_eis_data()
        #st.write(eis)
        points = DB.get_all_eis_points()

        wert_spalten = ['im_max', 're_min', 're_max', 'im_min', 'phase_max', 'phase_min', 'im_zif', 'phase_zif', 'mpd']
        df_long = points.melt(
            id_vars=['soc', 'zelle', 'cycle'],  # diese bleiben unverändert
            value_vars=wert_spalten,  # diese Spalten werden umgeformt
            var_name='parameter',  # neue Spalte für den Parameternamen
            value_name='wert'  # neue Spalte für den Wert
        )
        agg_funcs = {
            'wert': ['mean', 'std', 'median', 'min', 'max', rel_dev_to_median]
        }

        ops = ['soc_geo','overall_geo', 'tab overall']
        sel1 = st.segmented_control("Plots wählen", options=ops, default=ops[0])
        if sel1 == 'soc_geo':
            plot_para_over_soc(df_long,agg_funcs)
        elif sel1 == 'overall_geo':
            plot_para_overall(df_long,agg_funcs)
        else:
            plot_tab_overall(df_long,agg_funcs)


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

def plot_para_over_soc(df_long,agg_funcs):
    # GroupBy nach Zelle, SoC und Parameter
    df_agg = df_long.groupby(['zelle', 'soc', 'parameter']).agg(agg_funcs)

    # Spaltennamen bereinigen
    df_agg.columns = ['mittelwert', 'std', 'median', 'min', 'max', 'rel_abw_median']

    # Index zurücksetzen
    df_agg = df_agg.reset_index()
    df_agg['cv'] = df_agg['std'] / df_agg['mittelwert']

    opt = ['cv', 'rel_abw_median']
    sel = st.segmented_control("Wert auswählen", options=opt)
    for zelle_id in df_agg['zelle'].unique():
        df_plot = df_agg[df_agg['zelle'] == zelle_id]
        fig = plot_points(df_plot, zelle_id, "soc", sel, "parameter")
        st.subheader(f"{zelle_id}")
        st.plotly_chart(fig)
        st.write(df_plot)

def plot_para_overall(df_long,agg_funcs):
    # GroupBy nach Zelle, SoC und Parameter
    df_long = df_long[df_long['zelle'] != 'U_VTC5A_007']
    df_agg = df_long.groupby(['parameter','soc']).agg(agg_funcs)

    # Spaltennamen bereinigen
    df_agg.columns = ['mittelwert', 'std', 'median', 'min', 'max', 'rel_abw_median']

    # Index zurücksetzen
    df_agg = df_agg.reset_index()
    df_agg['cv'] = df_agg['std'] / df_agg['mittelwert']

    opt = ['cv', 'rel_abw_median']
    sel = st.segmented_control("Wert auswählen", options=opt, default=opt[0])

    fig = plot_points(df_agg, "Overall", "soc", sel, "parameter")
    st.subheader("Overall")
    st.plotly_chart(fig)
    st.write(df_agg)

def plot_tab_overall(df_long,agg_funcs):
    df_long = df_long[~df_long['zelle'].isin(['U_VTC5A_007', 'JT_VTC_001', 'JT_VTC_002'])]
    df_agg = df_long.groupby(['parameter']).agg(agg_funcs)

    # Spaltennamen bereinigen
    df_agg.columns = ['mittelwert', 'std', 'median', 'min', 'max', 'rel_abw_median']

    # Index zurücksetzen
    df_agg = df_agg.reset_index()
    df_agg['cv'] = df_agg['std'] / df_agg['mittelwert']
    st.write(df_agg)