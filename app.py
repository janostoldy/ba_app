import streamlit as st
import pandas as pd

from app_pages.analyse import analyse_app
from src.user import User, get_known_user
from app_pages.home import home_app
from app_pages.DEIS import Plot_DEIS
from app_pages.eis import eis_app
from app_pages.points import points_app
from app_pages.db import add_data_app, edit_data_app
from app_pages.kapa import kapazitaet_app
from app_pages.analyse import analyse_app
from app_pages.dva import dva_app
from app_pages.zellen import add_zelle_app, show_zelle_app
from app_pages.eingang import eingang_app

# streamlit run c:/projects/ba_pipline/App.py
# streamlit run /Users/janostoldy/Documents/git_projecte/ba_pipline/app.py

st.set_page_config(layout="wide", page_icon="🔋", page_title="Analyse-Tool")

# Anmeldung
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = None

if "User" not in st.session_state:
    st.session_state["User"] = None

if st.session_state["authenticated"] is None:
    st.title("Login")

    with st.form("login_form"):
        username = st.text_input("Benutzername")
        password = st.text_input("Passwort", type="password")
        known_user = get_known_user()
        if st.form_submit_button("Anmelden"):
            known_user_entry = known_user[
                (known_user.name == username)
                & (known_user.password == password)
            ]
            if not known_user_entry.empty:
                st.success(f"Willkommen, {username}!")
                st.session_state["authenticated"] = True
                st.session_state["User"] = known_user_entry.object.values[0]
                st.session_state["user_info"] = {
                    "displayName": username,
                    "givenName": username,
                }
            else:
                st.session_state["authenticated"] = False
                st.error(
                    "Falscher Benutzername oder Passwort. Bitte versuchen Sie es erneut."
                )


if st.session_state["authenticated"]:
    # Seitenleiste generieren
    home_page = st.Page(home_app, title="Home", default=True, icon="👋")
    analyse_page = st.Page(analyse_app, title="Analyse", icon="📈")
    eingang_page = st.Page(eingang_app, title="Eingang", icon="📥")
    kapa_page = st.Page(kapazitaet_app, title="Kapazität", icon="📈")
    dva_page = st.Page(dva_app, title="DVA", icon="📈")
    eis_page = st.Page(eis_app, title="EIS", icon="📈")
    deis_page = st.Page(Plot_DEIS, title="DEIS", icon="📈")
    points_page = st.Page(points_app, title="Points", icon="📈")
    user = st.session_state["User"]
    if user.role == "user":
        zellen_page = st.Page(show_zelle_app, title="Zellen", icon="🔋")
        pg = st.navigation(
            {
                "Start": [home_page],
                "Anwendungen": [
                    analyse_page,
                    zellen_page,
                    eingang_page,
                    kapa_page,
                    dva_page,
                    eis_page,
                    deis_page,
                    points_page,
                ],
            }
        )
    elif user.role == "admin":
        add_data_page = st.Page(add_data_app, title="Daten hinzufügen", icon="📰")
        delete_data_page = st.Page(edit_data_app, title="Daten bearbeiten", icon="📰")
        zelle_page = st.Page(add_zelle_app, title="Zellen hinzufügen", icon="📰")
        pg = st.navigation(
            {
                "Start": [home_page],
                "Daten": [
                    add_data_page,
                    delete_data_page,
                    zelle_page,
                ],
                "Anwendungen": [
                    analyse_page,
                    eingang_page,
                    kapa_page,
                    dva_page,
                    eis_page,
                    deis_page,
                    points_page,
                ],
            }
        )
    pg.run()