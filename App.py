import streamlit as st
import pandas as pd
from Classes.datenbank import Database
from Classes.datenanalyse import EIS_Analyse
import os

# streamlit run /Users/janostoldy/Documents/git_projecte/ba_pipline/App.py
st.title("EIS App")

con1 = st.container(border=True)
con1.header("Connect to Database")
db_path = con1.text_input("Insert Database-Folder", placeholder="Volumes/ge95his/Datenbank", value = "Volumes/ge95his/Datenbank")

con2 = st.container(border=True)
con2.header("Analayze EIS Data")
cycle = con2.number_input("Insert a Start Cycle", min_value=0, max_value=1000, value=1, step=1)
folder = con2.text_input("Insert Data-Folder", value="/Volumes/ge95his/Rohdaten", placeholder="/Data")

if db_path:
    DB = Database("Eis_Analyse.db", db_path)
    DA = EIS_Analyse(DB)
    datei_liste = DB.query("SELECT DISTINCT Datei, Cycle FROM Datapoints")

dis_button = False
if folder and datei_liste:
    mpr_files = [f for f in os.listdir(folder) if f.endswith('.mpr')]
    if mpr_files:
        gespeicherte_dateien = [row[0] for row in datei_liste]
        nicht_gespeicherte_dateien = [f for f in mpr_files if f not in gespeicherte_dateien]
        nicht_gespeicherte_dateien = pd.DataFrame(
            [{'Datei': f, 'Größe (KB)': round(os.path.getsize(os.path.join(folder, f)) / 1024)} for f in nicht_gespeicherte_dateien]
        )

        nicht_gespeicherte_dateien.insert(0,"Auswählen", False)

        con2.write("Gefundene .mpr-Dateien, die noch nicht in der Datenbank sind:")
        # Dateneditor mit Checkbox pro Zeile
        edited_df = con2.data_editor(
            nicht_gespeicherte_dateien,
            num_rows="fixed",
            use_container_width=True,
            disabled=["Datei","Größe (KB)"],
            column_config={
                "Auswählen": st.column_config.CheckboxColumn(
                    "Auswählen", help="Wählen Sie die Zeilen aus, die Sie analysieren möchten."
                ),
                "Datei": st.column_config.TextColumn("Datei"),
            },
            hide_index = True,
        )

        selected_rows = edited_df[edited_df["Auswählen"]].copy()
        con2.write("Ausgewählte Zeilen:")
        con2.write(selected_rows["Datei"], height=200)

    else:
        con2.write("Keine .mpr-Dateien im angegebenen Ordner gefunden.")

if con2.button("Analyse", type="primary", use_container_width=True, disabled=dis_button):
    file_dir = [os.path.join(folder, f) for f in nicht_gespeicherte_dateien]
    Data = EIS_Analyse.analyze_data(mpr_files, cycle)

if 'datei_liste' in locals():
    df = pd.DataFrame(datei_liste)
    df.columns = ['Datei', 'Zyklus']
    st.write("Dateien in Datenbank:")
    st.dataframe(df)