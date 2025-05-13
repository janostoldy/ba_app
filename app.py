import streamlit as st
from app_pages.home import home_app
from app_pages.DEIS import Plot_DEIS
from app_pages.EIS import Plot_EIS
from app_pages.Points import Plot_Points
from app_pages.DB import datenbank_app

# streamlit run c:/projects/ba_pipline/App.py

st.set_page_config(layout="wide", page_icon=":battery:", page_title="Analyse-Tool")

# Seitenleiste generieren
home_page = st.Page(home_app, title="Home", default=True, icon="👋")
db_page = st.Page(datenbank_app, title="Datenbank", icon="📰")
eis_page = st.Page(Plot_EIS, title="EIS", icon="📈")
deis_page = st.Page(Plot_DEIS, title="DEIS", icon="📈")
points_page = st.Page(Plot_Points, title="Points", icon="📈")

pg = st.navigation(
    {
        "Start": [
            home_page,
            db_page
            ],
        "Anwendungen": [
            eis_page,
            deis_page,
            points_page,
        ],
    }
)
pg.run()