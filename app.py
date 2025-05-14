import streamlit as st
import pandas as pd
from src.user import User, get_known_user
from app_pages.home import home_app
from app_pages.DEIS import Plot_DEIS
from app_pages.EIS import Plot_EIS
from app_pages.Points import Plot_Points
from app_pages.DB import datenbank_app
from app_pages.zelle import zelle_app

# streamlit run c:/projects/ba_pipline/App.py
# streamlit run /Users/janostoldy/Documents/git_projecte/ba_pipline/app.py

st.set_page_config(layout="wide", page_icon=":battery:", page_title="Analyse-Tool")

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
    eis_page = st.Page(Plot_EIS, title="EIS", icon="📈")
    deis_page = st.Page(Plot_DEIS, title="DEIS", icon="📈")
    points_page = st.Page(Plot_Points, title="Points", icon="📈")
    user = st.session_state["User"]
    if user.role == "user":
        pg = st.navigation(
            {
                "Start": [home_page],
                "Anwendungen": [
                    eis_page,
                    deis_page,
                    points_page,
                ],
            }
        )
    elif user.role == "admin":
        db_page = st.Page(datenbank_app, title="Datenbank", icon="📰")
        zelle_page = st.Page(zelle_app, title="Zelle", icon="📰")
        pg = st.navigation(
            {
                "Start": [home_page],
                "Daten": [
                    db_page,
                    zelle_page
                ],
                "Anwendungen": [
                    eis_page,
                    deis_page,
                    points_page,
                ],
            }
        )
    pg.run()