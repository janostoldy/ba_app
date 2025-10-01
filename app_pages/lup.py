import plotly.express as px
import streamlit as st
import pandas as pd
from classes.datenbank import Database

def lup_app():
    st.title("Creat Look-Up-Table")
    DB = Database("lup")