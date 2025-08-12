import streamlit as st
from Classes.datenbank import Database
import pandas as pd
import plotly.express as px

def impedanz_app():
    st.title("Impedanz")
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

    con1 = st.container(border=False)
    options = ["Niqhist", "Bode-Re", "Bode-Im", "Bode-Phase"]
    plot = con1.segmented_control("Plots", options, default=options[0])
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

    colums = ["time", "voltage", "current", "temp", "delta_cap", "c_rate", "re", "im", "phase", "freq",
              "datei", "typ"]

    imp_data = pd.DataFrame()
    for plot in df.itertuples(index=False):
        data = DB.get_impedanz(plot.name,plot.c_rate)
        if data[0].typ == "Basitec":
            min_time = min(row.time for row in data)
            filtered_rows = [row for row in data if row.time == min_time]
        else:
            filtered_rows = data
        filtered_df = pd.DataFrame(filtered_rows, columns=colums)
        imp_data = pd.concat([imp_data, filtered_df], ignore_index=True)
        imp_data["c_rate"] = pd.to_numeric(imp_data["c_rate"], errors="coerce")

    for c in c_rates:
        con = st.container(border=False)
        con.subheader(f"{c}-C")
        data = imp_data[imp_data["c_rate"] == c]
        data = data[data["freq"] <= 1900]
        fig = px.line(data,
                      x=x_data,
                      y=y_data,
                      color="typ",
                      hover_data=['freq']
                      )
        con.plotly_chart(fig)
        con.write(data)


