import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def safion_app():
    st.title("Safion Ergebnisse")
    con1 = st.container(border=True)
    uploaded_file = con1.file_uploader("Datei Auswählen", type=["csv"], accept_multiple_files=True)
    dateinamen = [file.name for file in uploaded_file]
    if len(uploaded_file) != 0:
        st.subheader("Plot")
        sel = st.selectbox("Daten wählen",dateinamen,index=None)
        if sel is not None:
            up_file = next((file for file in uploaded_file if file.name == sel), None)
            dic = get_data(up_file, con1)
            on = st.toggle("Delete wrong Data",value=True)

        else:
            dic = get_all_data(uploaded_file,con1)
            on = False
        fig = go.Figure()
        fig1 = go.Figure()
        first_key = next(iter(dic.keys()))
        first_df = dic[first_key]["Metadaten"]
        meta_col = first_df.columns
        meta = pd.DataFrame(columns= meta_col)
        for file in dic:
            data = dic[file]["Daten"]
            metadata = dic[file]["Metadaten"]
            metadata["name"] = file

            if metadata["Time [s]"][0] > 20 and on:
                continue
            meta = pd.concat([meta, metadata], ignore_index=True)
            fig.add_trace(go.Scatter(
                x=data["ReZ"],
                y=data["ImZ"],
                name=file,
                line_shape='spline',
                customdata=data[["PhaseZ", "Freq"]],
                hovertemplate="ReZ: %{x}<br>ImZ: %{y}<br>PhaseZ: %{customdata[0]}<br>Freq: %{customdata[1]} Hz"
                              "<extra></extra>"
            ))
            fig1.add_trace(go.Scatter(y=data["Freq"], name=file, line_shape='spline'))
        if sel is None:
            fig.update_layout(legend=dict(
                yanchor="bottom",
                y=1,
                xanchor="left",
                x=0.01
            ))
        fig1.update_layout(legend=dict(
            yanchor="bottom",
            y=0.99,
            xanchor="left",
            x=0.01
        ))
        st.plotly_chart(fig)
        st.write(meta)
        st.subheader("Frequenzen")
        st.plotly_chart(fig1)

def get_all_data(uploaded_file, con):
    dic = {}
    for file in uploaded_file:
        df = pd.read_csv(file)

        first_row = df.head(1)

        # Metadaten und Daten trennen
        meta_columns = df.columns[:13]  # Die ersten 13 Spalten sind Metadaten
        data_columns = df.columns[13:]  # Die restlichen Spalten sind Daten

        data = pd.DataFrame()
        meta_data = first_row[meta_columns].values
        meta_data = pd.DataFrame(meta_data, columns=meta_columns)
        for i in range(0, len(data_columns), 4):
            data_group = first_row[data_columns[i:i + 4]].values
            data_df = pd.DataFrame(list(data_group))
            data = pd.concat([data, data_df], ignore_index=True)

        # Erstellen eines neuen DataFrames
        new_columns = ["ReZ", "ImZ", "PhaseZ", "Freq"]
        data.columns = new_columns
        data["ImZ"] = -data["ImZ"]
        dic[file.name] = {
            "Metadaten": meta_data,
            "Daten": data
        }
    return dic

def get_data(uploaded_file, con):
    dic = {}

    df = pd.read_csv(uploaded_file)

    # Metadaten und Daten trennen
    meta_columns = df.columns[:13]  # Die ersten 13 Spalten sind Metadaten
    data_columns = df.columns[13:]  # Die restlichen Spalten sind Daten

    new_columns = ["ReZ", "ImZ", "PhaseZ", "Freq"]

    for idx, row in df.iterrows():
        data = pd.DataFrame()

        meta_data = pd.DataFrame([row[meta_columns].values], columns=meta_columns)
        for i in range(0, len(data_columns), 4):
            data_group = row[data_columns[i:i + 4]].values
            data_df = pd.DataFrame(list(data_group))
            data = pd.concat([data, data_df], axis=1 ,ignore_index=True)
        # Erstellen eines neuen DataFrames
        data = data.T
        data.columns = new_columns
        data["ImZ"] = -data["ImZ"]

        dic[meta_data["Time [s]"].values[0]] = {
            "Metadaten": meta_data,
            "Daten": data
        }
    return dic