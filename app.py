import streamlit as st
from dotenv import load_dotenv
import os
import kaleido

from src.user import User, get_known_user
from app_pages.home import home_app
from app_pages.niquist import points_app, niqhist_app
from app_pages.db import add_data_app, edit_data_app
from app_pages.kapa import kapazitaet_app
from app_pages.biologic import biologic_app
from app_pages.dva import dva_app
from app_pages.zellen import add_zelle_app, show_zelle_app
from app_pages.pruefung import pruefung_app
from app_pages.safion import safion_app
from app_pages.impedanz import basytec_app

# streamlit run c:/projects/ba_pipline/app.py
# streamlit run /Users/janostoldy/Documents/git_projecte/ba_app/app.py
load_dotenv()
st.set_page_config(layout="wide", page_icon="🔋", page_title="Analyse-Tool")

# Anmeldung
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = None

if "User" not in st.session_state:
    st.session_state["User"] = None

if st.session_state["authenticated"] is None:
    st.title("Login")

    with st.form("login_form"):
        username = os.getenv("APP_USER")
        password = os.getenv("APP_PASSWORD")
        if username is None:
            username = st.text_input("Benutzername")
            password = st.text_input("Passwort", type="password")
        known_user = get_known_user()
        if st.form_submit_button("Anmelden") or os.getenv("APP_PASSWORD"):
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
    biologic_page = st.Page(biologic_app, title="Biologic", icon="📈")
    safion_page = st.Page(safion_app, title="Safion", icon="📈")
    eingang_page = st.Page(pruefung_app, title="Prüfungen", icon="📥")
    kapa_page = st.Page(kapazitaet_app, title="Kapazität", icon="📈")
    dva_page = st.Page(dva_app, title="DVA", icon="📈")
    niqhist_page = st.Page(niqhist_app, title="Niqhist", icon="📈")
    points_page = st.Page(points_app, title="Points", icon="📈")
    basytec_page = st.Page(basytec_app, title="Basytec", icon="📈")

    user = st.session_state["User"]
    if user.role == "user":
        zellen_page = st.Page(show_zelle_app, title="Zellen", icon="🔋")
        pg = st.navigation(
            {
                "Start": [home_page],
                "Analysen": [
                    biologic_page,
                    safion_page
                ],
                "Anwendungen": [
                    zellen_page,
                    eingang_page,
                    kapa_page,
                    niqhist_page,
                    dva_page,
                    points_page,
                    basytec_page,
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
                "Analysen": [
                    biologic_page,
                    safion_page
                ],
                "Anwendungen": [
                    eingang_page,
                    kapa_page,
                    niqhist_page,
                    dva_page,
                    points_page,
                    basytec_page,
                ],
            }
        )
    pg.run()