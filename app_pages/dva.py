import io

import plotly.express as px
import streamlit as st
import pandas as pd
from src.filtern import daten_filter
from src.plotting_functions import download_button

def dva_app():
    st.title("DVA Analysis")
    DB = st.session_state['DB']
    if DB is None:
        st.error("Keine Verbindung zur Datenbank")
        st.stop()
    alldata = DB.get_all_dva()
    con1 = st.container(border=True)
    cycle, zelle = daten_filter(con1, alldata)
    filt_data = alldata.iloc[0:0].copy()
    if not cycle or not zelle:
        st.warning("Keine Werte ausgewählt")
    else:
        con1 = st.container(border=False)
        key = 0

        for z in zelle:
            for c in cycle:
                con2 = st.container(border=False)
                con2.divider()
                file = DB.get_file(c, z,"DVA")
                filt_data = pd.concat([filt_data, file])
                data, points = DB.get_dva(file["name"].values[0])
                fig = plot_dva(data,file["name"].values[0])
                fig = plot_dva_points(fig, data, points)
                con2.plotly_chart(fig)
                space1, col1, col2 = con2.columns([1, 20, 3])
                df_points = pd.DataFrame(points["Value"].values.reshape(1, -1), columns=points["Point"].values)
                col1.dataframe(df_points, hide_index=True)
                download_button(col2,fig,key)
                key += 1

        con1.subheader("Ausgewählte Daten:")
        con1.write(filt_data)
        con1.subheader("Plots:")

def plot_dva(Data, name):
    # Plot erstellen
    fig = px.line(Data, x='QQomAh_smoove', y='calc_dV_dQ', title=f'Differential Voltage Analysis (DVA) von: {name}',
                  labels={'dV/dQ': 'dV/dQ (V/Ah)'})
    fig.update_layout(
        yaxis_title='dV/dQ (V/Ah)',
        xaxis_title='Kapazität (Ah)',
        template='simple_white',
    )
    fig.update_traces(line=dict(color="#e37222"))

    return fig

def plot_dva_points(fig, calc_Data, calc_Points):
    for _, row in calc_Points.iterrows():
        if not row['Point'] == 'Q0':
            if row['Point'] in ['Q2', 'Q3']:
                y_value = calc_Data.loc[calc_Data['QQomAh_smoove'] == row['X_Start'], 'calc_dV_dQ'].values[0]
                min_value = min(calc_Data['calc_dV_dQ'])
                fig.add_shape(
                    type="line",
                    x0=row['X_Start'],
                    x1=row['X_Start'],
                    y0=min_value,
                    y1=y_value*1.1,
                    line=dict(color="#64a0c8", width=2)
                )
            else:
                y_value = calc_Data.loc[calc_Data['QQomAh_smoove'] == row['X_End'], 'calc_dV_dQ'].values[0]
            fig.add_shape(
                type="line",
                x0=row['X_Start'],
                x1=row['X_End'],
                y0 = y_value,
                y1 = y_value,
                line=dict(color="#64a0c8", width=2)
            )

            fig.add_annotation(
                x=(row['X_Start'] + row['X_End']) / 2,
                y=y_value*1.05,
                text=row['Point'],
                showarrow=False,
                font=dict(color="#64a0c8", size=12)
            )
    return fig
