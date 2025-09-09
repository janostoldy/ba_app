import streamlit as st
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from galvani import BioLogic
import pandas as pd
from config import mes_spalten
from src.plotting_functions import get_linestyles

def biologic_app():
    with st.sidebar:
        side = st.radio(
            "Wähle eine Option",
            ("Allgemein", "Impedanz")
        )
    if side == "Allgemein":
        allgemein_app()
    else:
        imp_app()

def allgemein_app():
    st.title("Biologic Ergebnisse")
    con1 = st.container(border=True)
    uploaded_file = con1.file_uploader("Datei Auswählen", type=["mpr", "csv"])
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.mpr'):
            mpr_file = BioLogic.MPRfile(uploaded_file)
            df = pd.DataFrame(mpr_file.data)
            df = df.rename(columns=mes_spalten)
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)

    if 'df' in locals():
        st.dataframe(df)
        combination_line, combination_dot = get_linestyles()
        time_columns = [col for col in df.columns if 'time' in col.lower()]
        if time_columns:
            time = df[time_columns[0]]
            data = df.drop(time_columns[0], axis=1)
            fig = make_subplots(rows=len(data.columns), cols=1, shared_xaxes=True, vertical_spacing=0.02,
                                subplot_titles=data.columns)
            for i, col in enumerate(data.columns):
                color = combination_line[i % len(combination_line)]['color']
                # dash = combination_line[i % len(combination_line)]['line_style']
                dash = 'solid'
                fig.add_trace(go.Scatter(x=time, y=data[col], line=dict(color=color, dash=dash)), row=i + 1, col=1)
                fig.update_xaxes(title_text="time_columns[0]", row=i + 1, col=1)
                fig.update_yaxes(title_text=col, row=i + 1, col=1)
            fig.update_layout(height=400 * len(data.columns), width=1000, title_text="Zeitverlauf der Messwerte",
                              showlegend=False, hovermode="closest")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Keine Zeitspalte gefunden.")

def imp_app():
    st.title("Biologic Impedanz")
    con1 = st.container(border=True)
    uploaded_file = con1.file_uploader("Datei Auswählen", type=["mpr", "csv"])
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.mpr'):
            mpr_file = BioLogic.MPRfile(uploaded_file)
            df = pd.DataFrame(mpr_file.data)
            df = df.rename(columns=mes_spalten)
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)

    if 'df' in locals():
        if 'zohm' not in df.columns:
            raise Exception("Keine Eis-Daten")

        # Eis Messung
        start_eis_indices = df[(df['flags'] == 53) & (df['freqhz'] > 0)].index
        end_eis_indices = df[(df['flags'] == 85) & (df['freqhz'] > 0)].index
        if len(start_eis_indices) == 0 or len(end_eis_indices) == 0:
            raise Exception('No EIS data found in file or wrong flags.')
        eis_values = [df.loc[start:end].copy() for start, end in zip(start_eis_indices, end_eis_indices)]
        zero_soc = min(df.qqomah)
        eis_soc = round((df.qqomah[start_eis_indices - 1] - zero_soc) / 125) * 125
        eis_ImA = df.ima[start_eis_indices - 1]
        eis_Calc_ImA = round(eis_ImA / 1250) * 1250
        eis_C_Rate = round(eis_ImA / 2900, 2)
        start_time = df.times[start_eis_indices]

        imp_data = pd.DataFrame()
        for i, eis in enumerate(eis_values):
            # Real und Imaginärteil berechnen
            imp = pd.DataFrame()
            eis_phi = np.deg2rad(eis['phasezdeg'])
            imp['temp'] = eis['temperaturec']
            imp['zohm'] = eis['zohm']
            imp['freqhz'] = eis['freqhz']
            imp['qcharge'] = eis['qchargemah']
            imp['phase'] = eis['phasezdeg']
            imp['calc_rezohm'] = eis['zohm'] * np.cos(eis_phi.values)
            imp['calc_imzohm'] = eis['zohm'] * np.sin(eis_phi.values) * -1
            imp['calc_ima'] = eis_Calc_ImA.iloc[i]
            imp['c_rate'] = eis_C_Rate.iloc[i]
            imp['calc_times'] = eis['times'] - start_time.iloc[i]

            imp = imp[imp["freqhz"] < 1999]
            imp_data = pd.concat([imp_data, imp], ignore_index=True)

            con1 = st.container(border=False)
            con1.subheader(f"C-Rate: {eis_C_Rate.iloc[i]}")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=imp['calc_rezohm'],
                y=imp['calc_imzohm'],
            ))
            con1.plotly_chart(fig, use_container_width=True)
            con1.dataframe(imp)
