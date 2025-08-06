import streamlit as st
from Classes.datenbank import Database
import pandas as pd

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
