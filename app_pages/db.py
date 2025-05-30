import streamlit as st
import pandas as pd
from Classes.datenbank import Database
from Classes.datenanalyse import EIS_Analyse
import os

def add_data_app():
    st.title("Daten hinzufügen")
    DB = st.session_state["DB"]
    DA = EIS_Analyse(DB)

    con2 = st.container(border=True)
    con2.header("Analayze EIS Data")
    alle_zellen = DB.query("SELECT DISTINCT id FROM Zellen")
    zelle = con2.selectbox("Zellen eingeben", alle_zellen)
    last_cycle = DB.query(f"SELECT MAX(Cycle) FROM Zellen WHERE id = '{zelle}'")
    last_cycle = last_cycle.values[0][0] if not last_cycle.empty else 1
    cycle = con2.number_input("Insert a Start Cycle", min_value=0, max_value=1000, value=last_cycle, step=1)
    folder = con2.text_input("Insert Data-Folder", value="/Volumes/ftm/EV_Lab_BatLab/02_Messexport/Urban/02_EIS/02_BioLogic/Sony US18650VTC5A/Charakterisierung/U_VTC5A_007", placeholder="/Data")

    datei_liste = DB.query("SELECT DISTINCT Datei, Cycle FROM Datapoints")

    dis_button = False
    if folder:
        mpr_files = [f for f in os.listdir(folder) if f.endswith('.mpr')]
        if mpr_files:
            gespeicherte_dateien = [row[0] for row in datei_liste]
            nicht_gespeicherte_dateien = [f for f in mpr_files if f not in gespeicherte_dateien]
            nicht_gespeicherte_dateien = pd.DataFrame(
                [{'Datei': f, 'Größe (KB)': round(os.path.getsize(os.path.join(folder, f)) / 1024)} for f in
                 nicht_gespeicherte_dateien]
            )

            nicht_gespeicherte_dateien.insert(0, "Auswählen", False)

            con2.write("Gefundene .mpr-Dateien, die noch nicht in der Datenbank sind:")
            # Dateneditor mit Checkbox pro Zeile
            edited_df = con2.data_editor(
                nicht_gespeicherte_dateien,
                num_rows="fixed",
                use_container_width=True,
                disabled=["Datei", "Größe (KB)"],
                column_config={
                    "Auswählen": st.column_config.CheckboxColumn(
                        "Auswählen", help="Wählen Sie die Zeilen aus, die Sie analysieren möchten."
                    ),
                    "Datei": st.column_config.TextColumn("Datei"),
                },
                hide_index=True,
            )

            selected_rows = edited_df[edited_df["Auswählen"]].copy()
            con2.write("Ausgewählte Zeilen:")
            con2.dataframe(selected_rows["Datei"], height=200)

            if con2.button("Analyse", type="primary", use_container_width=True, disabled=dis_button):
                try:
                    file_dir = [os.path.join(folder, f) for f in selected_rows["Datei"]]
                    with st.spinner("Analysieren...",show_time=True):
                        cycle = DA.analyze_data(file_path=file_dir, cycle=cycle, Zelle=zelle, save_data=False)
                        con2.success("Daten erfolgreich in Datenbank gespeichert.")
                except Exception as e:
                    con2.error(f"Fehler beim Analysieren: {e}")
        else:
            con2.write("Keine .mpr-Dateien im angegebenen Ordner gefunden.")



    if 'datei_liste' in locals():
        df = pd.DataFrame(datei_liste)
        df.columns = ['Datei', 'Zyklus']
        st.write("Dateien in Datenbank:")
        st.dataframe(df)

def delete_data_app():
    st.title("Daten löschen")

    con1 = st.container(border=True)
    con1.header("Data Filtern")
    zelle = con1.text_input("Insert a Cell Name", placeholder="SN0001", value="SN0001")
    cyle = con1.number_input("Insert a Start Cycle", min_value=0, max_value=1000, value=1, step=1)
    DB = st.session_state["DB"]
    data = DB.query(f"SELECT * FROM Datapoints")
    con1.dataframe(data)