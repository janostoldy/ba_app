import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def safion_app():
    st.title("Safion Ergebnisse")
    con1 = st.container(border=True)
    uploaded_file = con1.file_uploader("Datei Auswählen", type=["csv"],)
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        with st.expander("Daten anzeigen",expanded=False):
            st.dataframe(df)

        mean_row = df.mean()

        # Metadaten und Daten trennen
        meta_columns = df.columns[:13]  # Die ersten 13 Spalten sind Metadaten
        data_columns = df.columns[13:]  # Die restlichen Spalten sind Daten

        data = []
        meta_data = [mean_row[meta_columns].values]
        meta_data  = pd.DataFrame(meta_data, columns=meta_columns)
        for i in range(0, len(data_columns), 4):
            data_group = mean_row[data_columns[i:i + 4]].values
            data.append(list(data_group))

        # Erstellen eines neuen DataFrames
        new_columns = ["ReZ", "ImZ", "PhaseZ", "Freq"]
        reshaped_df = pd.DataFrame(data, columns=new_columns)
        reshaped_df["ImZ"] = -reshaped_df["ImZ"]

        dic = {
            "Metadaten": meta_data,
            "Daten": reshaped_df
        }

        st.subheader("Plot")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=reshaped_df["ReZ"], y=reshaped_df["ImZ"], name="Niqhist-Kurve",line_shape='spline'))

        st.plotly_chart(fig)
        with st.expander("Reshaped-Daten anzeigen", expanded=False):
            st.write(meta_data)
            st.dataframe(reshaped_df)

        st.subheader("Frequenzen")
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(y=reshaped_df["Freq"], name="Frequenezen", line_shape='spline'))
        st.plotly_chart(fig1)


safion_app()