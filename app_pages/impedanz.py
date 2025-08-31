import streamlit as st
from galvani import BioLogic

from classes.datenbank import Database
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.interpolate import interp1d
from src.plotting_functions import colors_short

def basytec_app():
    with st.sidebar:
        side = st.radio(
            "Wähle eine Option",
            ("Berechnen", "Vergleichen")
        )
    if side == "Berechnen":
        berechnen_app()
    else:
        vergleichen_app()

def berechnen_app():
    st.title("Basytec - Calc")
    DB = Database("Impedanz")

    files = DB.get_imp_files()
    data = []
    c_rates = []
    for f in files.itertuples(index=False):
        c_rate = DB.get_imp_rate(f.name)
        for c in c_rate:
            if float(c[0]) not in c_rates:
                c_rates.append(float(c[0]))
            row = f._asdict()
            row["c_rate"] = float(c[0])
            data.append(row)
    df = pd.DataFrame(data)
    st.write(df)
    colums = ["time", "voltage", "current", "temp", "delta_cap", "c_rate", "re", "im", "phase", "freq",
              "datei", "typ"]
    imp_data = pd.DataFrame()
    for plt in df.itertuples(index=False):
        data = DB.get_impedanz(plt.name,plt.c_rate)
        if data[0].typ == "Basytec":
            min_time = min(row.time for row in data)
            filtered_rows = [row for row in data if row.time == min_time]
        else:
            filtered_rows = data
        filtered_df = pd.DataFrame(filtered_rows, columns=colums)
        filtered_df = filtered_df.sort_values('freq')
        imp_data = pd.concat([imp_data, filtered_df], ignore_index=True)
        imp_data["c_rate"] = pd.to_numeric(imp_data["c_rate"], errors="coerce")

    imp_data = imp_data.drop(imp_data[(imp_data["typ"] == "Biologic") & (imp_data["freq"] == 1001.9983)].index)
    con1 = st.container(border=False)

    col1, col2 = con1.columns(2)
    options = ["Niqhist", "Bode-Re", "Bode-Im", "Bode-Phase","Basy"]
    plot = col1.segmented_control("Plots", options, default=options[0])
    col2_1 ,col2_2 = col2.columns(2)
    fmin = col2_1.number_input("F_min",0,2000)
    fmax = col2_2.number_input("F_max",0,2000)
    cut = col2.toggle("Niedrige und Hohe Frequenzen schneiden")
    dis = False if plot != "Basy" else True
    calc = col1.toggle("Calc_Field", disabled=dis)
    lut_impedanz = pd.DataFrame()
    options = ["Setup", "C-Rate"]
    subplot = col1.segmented_control("Subplots", options, default=options[0])

    if calc or dis:
        for c in c_rates:
            data = imp_data[imp_data["c_rate"] == c]
            data = data[data["freq"] <= 1900]
            basy = data[data["typ"] == "Basytec"]
            biol = data[data["typ"] == "Biologic"]

            re_f_basy = interp1d(basy["freq"], basy["re"],kind='quadratic', fill_value='extrapolate')
            re_f_biol = interp1d(biol["freq"], biol["re"],kind='quadratic', fill_value='extrapolate')
            im_f_basy = interp1d(basy["freq"], basy["im"], kind='quadratic', fill_value='extrapolate')
            im_f_biol = interp1d(biol["freq"], biol["im"], kind='quadratic', fill_value='extrapolate')

            x_common = np.linspace(min(basy["freq"].min(), biol["freq"].min()),max(basy["freq"].max(), biol["freq"].max()),200)

            re_inter_basy = re_f_basy(x_common)
            re_inter_biol = re_f_biol(x_common)
            im_inter_basy = im_f_basy(x_common)
            im_inter_biol = im_f_biol(x_common)

            Z_basy = re_inter_basy + 1j * im_inter_basy
            Z_biol = re_inter_biol + 1j * im_inter_biol

            Y_total = 1 / Z_basy - 1 / Z_biol
            Z_total = 1 / Y_total

            re_diff = Z_total.real
            im_diff = Z_total.imag
            ph_diff = np.arctan2(im_diff, re_diff)

            diff_frame = pd.DataFrame({
                "time": 0,
                "voltage": 0,
                "current": 2.9*c,
                "temp": 26,
                "delta_cap": 0,
                "c_rate": c,
                "re": re_diff,
                "im": im_diff,
                "phase": ph_diff,
                "freq": x_common,
                "datei": "Berechnet",
                "typ": "calc"
            })
            lut_data = pd.DataFrame({
                "c_rate": c,
                "re": re_diff,
                "im": im_diff,
                "phase": ph_diff,
                "freq": x_common,
            })
            lut_impedanz = pd.concat([lut_impedanz, lut_data], ignore_index=True)
            imp_data = pd.concat([imp_data, diff_frame], ignore_index=True)

    if cut:
        imp_data = imp_data[imp_data["freq"] <= fmax]
        imp_data = imp_data[imp_data["freq"] >= fmin]
        lut_impedanz = lut_impedanz[lut_impedanz["freq"] <= fmax]
        lut_impedanz = lut_impedanz[lut_impedanz["freq"] >= fmin]

    if plot == "Niqhist":
        x_data = "re"
        y_data = "im"
    elif plot == "Bode-Re":
        x_data = "freq"
        y_data = "re"
    elif plot == "Bode-Im":
        x_data = "freq"
        y_data = "im"
    elif plot == "Bode-Phase":
        x_data = "freq"
        y_data = "phase"
    elif plot == "Basy":
        if con1.button("In DB speichern", type='secondary', use_container_width=True):
            DB.df_in_DB(lut_impedanz,'basytec')
        plot_basy(lut_impedanz)
        con = st.container()
        con.subheader("Ersatzschaltbild")
        con.image("src/pic/basytec.png")
        subplot = "Pass"

    if subplot == "Setup":
        plot_c_rates(imp_data, x_data, y_data, c_rates)
    elif subplot == "C-Rate":
        plot_typ(imp_data, x_data, y_data)


def vergleichen_app():
    st.title("Basytec - Compare")
    DB = Database("Comp")
    xcts = DB.get_basytec()
    con1 = st.container(border=True)
    con1.subheader("Messung")
    basy_file = con1.file_uploader("Datei Auswählen", type=["csv"], accept_multiple_files=False)
    con1.subheader("Vergleichswerte")
    bio_file = con1.file_uploader("Datei Auswählen", type=["mpr"], accept_multiple_files=False)

    if basy_file is not None:
        basy_data = pd.read_csv(basy_file)
        st.write(basy_data)

    if bio_file is not None:
        bio_data = pd.DataFrame()
        mpr_file = BioLogic.MPRfile(bio_file)
        bio_data_imp = pd.DataFrame(mpr_file.data)
        bio_data['freq'] = bio_data_imp['freq/Hz']
        z = bio_data_imp['|Z|/Ohm']
        bio_data['phase'] = bio_data_imp['Phase(Z)/deg']
        bio_data['re'] = z * np.cos(bio_data['phase'])
        bio_data['im'] = z * np.sin(bio_data['phase'])
        bio_data['c_rate'] = round(bio_data_imp['I/mA']/2500 / 1250) * 1250

    if bio_file is not None and basy_file is not None:
        c_rate = basy_data['c_rate'].unique()
        for c in c_rate:
            bio_c = bio_data[bio_data['c_rate'] == c]
            basy_c = basy_data[basy_data['c_rate'] == c]
            xcts_c = xcts[xcts['c_rate'] == 0.25]

            re_f_basy = interp1d(basy_c["freq"], basy_c["re"], kind='quadratic', fill_value='extrapolate')
            re_f_xcts = interp1d(xcts_c["freq"], xcts_c["re"], kind='quadratic', fill_value='extrapolate')
            im_f_basy = interp1d(basy_c["freq"], basy_c["im"], kind='quadratic', fill_value='extrapolate')
            im_f_xcts = interp1d(xcts_c["freq"], xcts_c["im"], kind='quadratic', fill_value='extrapolate')

            x_common = np.linspace(min(basy_c["freq"].min(), bio_c["freq"].min()),
                                   max(basy_c["freq"].max(), bio_c["freq"].max()), 200)

            re_inter_basy = re_f_basy(x_common)
            re_inter_xcts = re_f_xcts(x_common)
            im_inter_basy = im_f_basy(x_common)
            im_inter_xcts = im_f_xcts(x_common)

            Z_basy = re_inter_basy + 1j * im_inter_basy
            Z_xcts = re_inter_xcts + 1j * im_inter_xcts

            Y_total = 1 / Z_basy - 1 / Z_xcts
            Z_total = 1 / Y_total

            re_diff = Z_total.real
            im_diff = Z_total.imag
            ph_diff = np.arctan2(im_diff, re_diff)
            calc_c = pd.DataFrame({
                're': re_diff,
                'im': im_diff,
                'phase': ph_diff,
                'c_rate': c,
                'freq': x_common,
            })

            st.write("Realteil")
            plot_comp(basy_c, bio_c, calc_c, 're')
            st.write("Imaginärteil")
            plot_comp(basy_c, bio_c, calc_c, 'im')
            st.write("Phase")
            plot_comp(basy_c, bio_c, calc_c, 'phase')

def plot_typ(imp_data, x, y):
    for t in ["Basytec","Biologic"]:
        con = st.container(border=False)
        con.subheader(t)
        data = imp_data[imp_data["typ"] == t]
        data = data[data["freq"] <= 1900]
        log = True if y == "freq" else False

        fig = px.line(data,
                      x=x,
                      log_x=log,
                      y=y,
                      color="c_rate",
                      color_discrete_sequence=list(colors_short.values()),
                      hover_data=['freq']
                      )
        con.plotly_chart(fig)
        con.write(data)

def plot_c_rates(imp_data, x, y, c_rates, ):
    for c in c_rates:
        con = st.container(border=False)
        con.subheader(f"{c}-C")
        data = imp_data[imp_data["c_rate"] == c]
        data = data[data["freq"] <= 1900]
        log = True if y == "freq" else False

        fig = px.line(data,
                      x=x,
                      log_x=log,
                      y=y,
                      color="typ",
                      color_discrete_sequence=list(colors_short.values()),
                      hover_data=['freq']
                      )
        con.plotly_chart(fig)
        con.write(data)

def plot_basy(data):
    con = st.container(border=False)
    fig1 = px.line(data,
                   x="freq",
                   log_x=True,
                   y="re",
                   color="c_rate",
                   hover_data=['freq'],
                   )
    fig2 = px.line(data,
                   x="freq",
                   log_x=True,
                   y="im",
                   color="c_rate",
                   hover_data=['freq']
                   )
    fig3 = px.line(data,
                   x="freq",
                   log_x=True,
                   y="phase",
                   color="c_rate",
                   hover_data=['freq']
                   )

    con.subheader(f"Realteil")
    con.plotly_chart(fig1)
    con.subheader(f"Imaginärteil")
    con.plotly_chart(fig2)
    con.subheader(f"Phase")
    con.plotly_chart(fig3)

    con.subheader(f"Data")
    con.dataframe(data)

def plot_comp(basy, bio, calc_c, plt):
    con = st.container(border=False)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=calc_c['freq'],y=calc_c[plt], mode="lines",name="Berechnet"))
    fig.add_trace(go.Scatter(x=bio['freq'],y=bio[plt], mode="lines",name="Referenz"))
    fig.add_trace(go.Scatter(x=basy['freq'],y=basy[plt], mode="lines",name="Gemessen"))
    fig.update_xaxes(type="log")
    con.plotly_chart(fig)
