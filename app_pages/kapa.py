import plotly.express as px
import streamlit as st
import pandas as pd
import io
from src.filtern import daten_filter
from src.plotting_functions import colors

def kapazitaet_app():
    st.title("Kapazität")
    DB = st.session_state["DB"]
    alldata = DB.get_all_kapa()
    con0 = st.container(border=True)
    cycle, zelle = daten_filter(con0, alldata)
    filt_data = pd.DataFrame()
    if not cycle or not zelle:
        st.warning("Keine Werte ausgewählt")
    else:
        con1 = st.container(border=False)
        data = pd.DataFrame()
        for z in zelle:
            for c in cycle:
                file = DB.get_file(c, z,"Kapa")
                kap = DB.get_kapa(file["name"].values[0])
                filt_data = pd.concat([filt_data, kap])
                data = pd.concat([data, kap])

        con1.subheader("Ausgewählte Daten:")
        con1.write(filt_data)
        con1.subheader("Plots:")

        selected = con1.toggle("Alle Grafen in einem Plot")
        if selected :
            plots = ["Allen Zellen"]
            plot_name = ""
            data_mod = data
            subplots = "Zelle"
            einheit = "mAh"
        else:
            plots = zelle
            plot_name = "Zelle"
            subplots = "Zelle"
            einheit = "mAh"

        key = 0
        for p in plots:
            con2 = st.container(border=False)
            con2.divider()
            if not selected:
                data_mod = data[data[plot_name] == p]
            name = f"Kapazität von {plot_name} {p} in {einheit}"
            fig = plot_kapa(data_mod, name,subplots)
            con2.plotly_chart(fig)
            fig.update_layout(
                template="plotly",  # <- wichtig!
                paper_bgcolor='white',
                plot_bgcolor='white',
                font_color='black',
                legend_title_font_color='black',
                xaxis=dict(
                    showgrid=True,
                    gridcolor='#e0e0e0',  # Farbe des Grids
                    gridwidth=1  # Dicke der Linien
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='#e0e0e0',
                    gridwidth=1
                )
            )

            # --- Export als SVG ---
            # Temporären Buffer für SVG-Datei anlegen
            svg_buffer = io.BytesIO()
            fig.write_image(svg_buffer, format='svg', engine='kaleido', width=1200, height=800)
            svg_data = svg_buffer.getvalue()
            space, col2 = con2.columns([4, 1])
            col2.download_button(
                label="Download als SVG",
                data=svg_data,
                file_name="plot.svg",
                mime="image/svg+xml",
                key=key,
                use_container_width=True
            )
            key += 1

            con2.dataframe(data_mod)


def plot_kapa(data,name,subplots):
    fig = px.line(data,
                  x="Cycle",
                  y="Kapa",
                  color=subplots,
                  title=name,
                  markers=True,
                  color_discrete_sequence=list(colors.values())
                  )
    fig.update_layout(
        yaxis_title='Kapazirät (mAh)',
        xaxis_title='Zyklken',
        template='simple_white'
    )
    return fig
