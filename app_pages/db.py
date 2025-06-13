import streamlit as st
import pandas as pd
import numpy as np

from src.filtern import daten_filer
from src.plotting_df import highlight_status, status_func
from Classes.datenanalyse import Analyse
import os

def add_data_app():
    st.title("Daten hinzufügen")
    DB = st.session_state["DB"]
    DA = Analyse(DB)

    con2 = st.container(border=True)
    con2.header("Analayze EIS Data")
    folder = con2.text_input("Daten-Ordner eingeben", value="/Volumes/ftm/EV_Lab_BatLab/02_Messexport/Urban/02_EIS/02_BioLogic/Sony US18650VTC5A/Charakterisierung/U_VTC5A_007", placeholder="/Data")
    alle_zellen = DB.get_all_zells()
    zelle = con2.selectbox("Zellen eingeben", alle_zellen)
    typs = ["EIS/Ageing-Analyse","DVA-Analyse","Kapazitäts-Messung"]
    typ = con2.selectbox("Analyse Art",typs)
    last_cycle = DB.get_zell_cycle(zelle)
    last_cycle = last_cycle.values[0][0] if not last_cycle.empty else 1
    cycle = con2.number_input("Zyklus eingeben", min_value=0, max_value=1000, value=last_cycle, step=1)

    try:
        datei_liste = DB.get_all_files()
    except Exception as e:
        con2.error(f"Fehler beim Abrufen der Datenbank: {e}")
        datei_liste = None

    dis_button = False
    if datei_liste is not None:
        try:
            with st.spinner("Daten suchen...", show_time=True):
                mpr_files = [f for f in os.listdir(folder) if f.endswith('.mpr')]
        except Exception as e:
            con2.error(f"Fehler beim Abrufen der Dateien im Ordner: {e}")
            mpr_files = None
        if mpr_files is not None:
            # DF mit allen Dateien und Status und gefilterten Dateien
            gespeicherte_dateien = datei_liste['name'].values
            import_files = pd.DataFrame([{'Datei': f,'Größe (KB)': round(os.path.getsize(os.path.join(folder, f)) / 1024)} for f in mpr_files])
            import_files["Status"] = import_files["Datei"].apply(lambda f: status_func(f, gespeicherte_dateien, folder))
            col1, col2 = con2.columns([4,1])
            col1.write("Gefundene .mpr-Dateien")
            filter = col2.selectbox(
                "Status",
                ("Neu","In Datenbank","Fehlende Daten"),
                label_visibility="collapsed",
                index=None,
                placeholder="Filter wählen...",

            )
            # Filter anwenden, wenn ausgewählt
            if filter:
                filter_files = import_files[import_files["Status"] == filter]
            else:
                filter_files = import_files

            if "filter_files" not in st.session_state or st.session_state.filter_files.equals(filter_files) == False:
                 st.session_state.filter_files = filter_files
            event = con2.dataframe(
                st.session_state.filter_files.style.map(highlight_status, subset=["Status"]),
                key="data",
                on_select="rerun",
                selection_mode="multi-row",
            )
            selected_rows = st.session_state.filter_files.iloc[event.selection.rows]
            if con2.button("Analyse", type="primary", use_container_width=True, disabled=dis_button):
                try:
                    file_dir = [os.path.join(folder, f) for f in selected_rows["Datei"]]
                    with st.spinner("Analysieren...",show_time=True):
                        if typ == "EIS/Ageing-Analyse":
                            DA.analyze_EIS_data(file_path=file_dir, cycle=cycle, Zelle=zelle, save_data=True)
                        elif typ == "DVA-Analyse":
                            DA.analys_OCV_data(file_path=file_dir, cycle=cycle, Zelle=zelle, save_data=True)
                        con2.success("Daten erfolgreich in Datenbank gespeichert.")
                        st.rerun()
                except Exception as e:
                    con2.error(f"Fehler bei {typ}: {e}")
        else:
            con2.error("Keine .mpr-Dateien im angegebenen Ordner gefunden.")

    if 'datei_liste' in locals():
        #df.columns = ['Datei', 'Zyklus', 'Zelle']
        st.write("Dateien in Datenbank:")
        st.dataframe(datei_liste)

@st.dialog("Löschen bestätigen",width="small")
def file_loeschen(files):
    st.write("Wollen sie die Zelle wirklich löschen?")
    DB = st.session_state["DB"]
    st.write(files)
    if st.button("Endgültig Löschen", type="primary", use_container_width=True):
        for f in files:
            DB.delete_file(f)
        st.rerun()

@st.dialog("Daten bearbeiten",width="large")
def file_bearbeiten(files):
    st.write("Noch nicht fertig, ändert nur Files")
    DB = st.session_state["DB"]
    alle_zellen = DB.get_all_zells()
    alle_typen = DB.get_file_typs()
    for index, row in files.iterrows():
        st.divider()
        con = st.container()
        con.write(f"Datei {row['name']} bearbeiten:")
        info = con.text_input("Datei Infos", value=row["Info"], key=index*5)
        col2, col3, col4, col5 = con.columns([3,3,2,2])
        cycle = col2.number_input("Zyklus", value=row["Cycle"], min_value=0, step=1, key=index*5+1)
        ind1 = np.where(alle_zellen == row["Zelle"])[0][0]
        zelle = col3.selectbox("Zellen eingeben", alle_zellen, index=int(ind1), key=index*5+2)
        ind2 = np.where(alle_typen == row["Typ"])[0][0]
        typ = col4.selectbox("Typ", alle_typen, index=int(ind2), key=index*5+3)
        col5.subheader("")
        if col5.button("Bestätigen", type="primary", use_container_width=True, key=index*5+4):
            try:
                DB.insert_file(row["name"], cycle, info, zelle)
                st.rerun()
            except Exception as e:
                con.error(f"Fehler beim ändern der Daten: {e}")

def edit_data_app():
    st.title("Daten bearbeiten")
    DB = st.session_state["DB"]

    con1 = st.container(border=True)
    data = (DB.get_all_files())
    cycle, zelle = daten_filer(con1,data)
    data = pd.DataFrame()
    for zel in zelle:
        for cyc in cycle:
            dat = DB.get_file(cyc, zel, typ="*")
            data = pd.concat([data, dat], ignore_index=True)

    st.session_state.filter_files = data

    event = con1.dataframe(
        st.session_state.filter_files,
        key="data",
        on_select="rerun",
        selection_mode="multi-row",
    )
    selected_rows = st.session_state.filter_files.iloc[event.selection.rows]

    col1, col2 = con1.columns([1,4])
    if col1.button("Löschen", type="secondary", use_container_width=True):
        if selected_rows.empty:
            con1.warning("Keine Daten ausgewählt!")
        else:
            file_loeschen(selected_rows["name"])
    if col2.button("Bearbeiten", type="primary", use_container_width=True):
        if selected_rows.empty:
            con1.warning("Keine Daten ausgewählt!")
        else:
            file_bearbeiten(selected_rows)