import streamlit as st
import pandas as pd

def safion_app():
    st.title("Safion Ergebnisse")
    con1 = st.container(border=True)
    uploaded_file = con1.file_uploader("Datei Auswählen", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        con1.dataframe(df)
        for row in df.itertuples():
            st.write(row)

safion_app()