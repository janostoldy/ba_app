import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def safion_app():
    st.title("Safion Ergebnisse")
    con1 = st.container(border=True)
    dic = get_data(con1)
    if len(dic) != 0:
        st.subheader("Plot")

        sel = st.selectbox("Daten wählen",dic.keys(),index=None)
        if sel is not None:
            data = dic[sel]["Daten"]
            metadata = dic[sel]["Metadaten"]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data["ReZ"], y=data["ImZ"], name="Niqhist-Kurve",line_shape='spline'))

            st.plotly_chart(fig)
            st.write(metadata)
            with st.expander("Reshaped-Daten anzeigen", expanded=False):
                st.dataframe(data)

            st.subheader("Frequenzen")
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(y=data["Freq"], name="Frequenezen", line_shape='spline'))
            st.plotly_chart(fig1)
        else:
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
                pd.concat([meta, metadata], ignore_index=True)
                fig.add_trace(go.Scatter(x=data["ReZ"], y=data["ImZ"], name=file, line_shape='spline'))
                fig1.add_trace(go.Scatter(y=data["Freq"], name=file, line_shape='spline'))
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

def get_data(con):
    uploaded_file = con.file_uploader("Datei Auswählen", type=["csv"], accept_multiple_files=True)
    if uploaded_file is not None:
        dic = {}
        for file in uploaded_file:
            df = pd.read_csv(file)

            mean_row = df.mean()

            # Metadaten und Daten trennen
            meta_columns = df.columns[:13]  # Die ersten 13 Spalten sind Metadaten
            data_columns = df.columns[13:]  # Die restlichen Spalten sind Daten

            data = []
            meta_data = [mean_row[meta_columns].values]
            meta_data = pd.DataFrame(meta_data, columns=meta_columns)
            for i in range(0, len(data_columns), 4):
                data_group = mean_row[data_columns[i:i + 4]].values
                data.append(list(data_group))

            # Erstellen eines neuen DataFrames
            new_columns = ["ReZ", "ImZ", "PhaseZ", "Freq"]
            reshaped_df = pd.DataFrame(data, columns=new_columns)
            reshaped_df["ImZ"] = -reshaped_df["ImZ"]

            dic[file.name] = {
                "Metadaten": meta_data,
                "Daten": reshaped_df
            }
        return dic