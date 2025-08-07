import streamlit as st
from Classes.datenbank import Database
import pandas as pd
import plotly.graph_objects as go

def impedanz_app():
    st.title("Impedanz")
    DB = Database("Impedanz")
    files = DB.get_imp_files()
    data = []
    for f in files.itertuples(index=False):
        c_rate = DB.get_imp_rate(f.name)
        for c in c_rate:
            row = f._asdict()
            row["c_rate"] = float(c[0])
            data.append(row)
    df = pd.DataFrame(data)
    st.write(df)

    imp_data = []
    for plot in df.itertuples(index=False):
        data = DB.get_impedanz(plot.name,plot.c_rate)
        if data[0].typ == "Basitec":
            min_time = min(row.time for row in data)
            filtered_rows = [row for row in data if row.time == min_time]
        else:
            filtered_rows = data
        imp_data.append(filtered_rows)
    st.write(imp_data)


