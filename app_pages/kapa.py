import plotly.express as px
import streamlit as st
import pandas as pd
import io
from src.filtern import kapa_filter, daten_filer

def kapazität_app():
    st.title("Kapazität")
    DB = st.session_state["DB"]
    alldata = DB.get_all_kapa()
    con1 = st.container(border=True)
    cycle, zelle = daten_filer(con1,alldata)
    filt_data = pd.DataFrame()
    if not cycle or not zelle:
        st.warning("Keine Werte ausgewählt")
    else:
        con1 = st.container(border=False)
        key = 0
        for z in zelle:
            con2 = st.container(border=False)
            con2.divider()
            data = pd.DataFrame()
            for c in cycle:
                file = DB.get_file(c, z,"Kapa")
                kap = DB.get_kapa(file["name"].values[0])
                filt_data = pd.concat([filt_data, kap])
                data = pd.concat([data, kap])
            fig = plot_kapa(data,z)
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
                use_container_width = True
            )
            key += 1

            con2.dataframe(data)

        con1.subheader("Ausgewählte Daten:")
        con1.write(filt_data)
        con1.subheader("Plots:")


def plot_kapa(data,name):
    fig = px.scatter(data, x="Cycle", y="Kapa",title=f"Kapazität von Zelle {name}")
    fig.update_layout(
        yaxis_title='Kapazirät (Ah)',
        xaxis_title='Zyklken',
        template='simple_white'
    )
    return fig
