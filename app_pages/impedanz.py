import streamlit as st

from classes.datenbank import Database
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.interpolate import interp1d

def basytec_app():
    st.title("Basytec")
    DB = Database("Impedanz")

    with st.sidebar:
        radio = st.radio(
            "Wähle eine Option",
            ("Berechnen", "Vergleichen")
        )

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
        if data[0].typ == "Basitec":
            min_time = min(row.time for row in data)
            filtered_rows = [row for row in data if row.time == min_time]
        else:
            filtered_rows = data
        filtered_df = pd.DataFrame(filtered_rows, columns=colums)
        imp_data = pd.concat([imp_data, filtered_df], ignore_index=True)
        imp_data["c_rate"] = pd.to_numeric(imp_data["c_rate"], errors="coerce")

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
    if calc or dis:
        for c in c_rates:
            data = imp_data[imp_data["c_rate"] == c]
            data = data[data["freq"] <= 1900]
            basy = data[data["typ"] == "Basitec"]
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
        plot_curves(imp_data, x_data, y_data, c_rates)
    elif plot == "Bode-Re":
        x_data = "freq"
        y_data = "re"
        plot_curves(imp_data, x_data, y_data, c_rates)
    elif plot == "Bode-Im":
        x_data = "freq"
        y_data = "im"
        plot_curves(imp_data, x_data, y_data, c_rates)
    elif plot == "Bode-Phase":
        x_data = "freq"
        y_data = "phase"
        plot_curves(imp_data, x_data, y_data, c_rates)
    elif plot == "Basy":
        if con1.button("In DB speichern", type='secondary', use_container_width=True):
            DB.df_in_DB(lut_impedanz,'basytec')
        plot_basy(lut_impedanz)
        con = st.container()
        con.subheader("Ersatzschaltbild")
        con.image("00_Test_Data/basytec.png")

def plot_curves(imp_data, x, y, c_rates):
    for c in c_rates:
        con = st.container(border=False)
        con.subheader(f"{c}-C")
        data = imp_data[imp_data["c_rate"] == c]
        data = data[data["freq"] <= 1900]
        fig = px.line(data,
                      x=x,
                      log_x=True,
                      y=y,
                      color="typ",
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

