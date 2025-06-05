import streamlit as st
import pandas as pd
from src.plotting_df import highlight_status, status_func
from Classes.datenanalyse import EIS_Analyse
import os

def add_data_app():
    st.title("Daten hinzufügen")
    DB = st.session_state["DB"]
    DA = EIS_Analyse(DB)

    con2 = st.container(border=True)
    con2.header("Analayze EIS Data")
    alle_zellen = DB.get_all_zells()
    zelle = con2.selectbox("Zellen eingeben", alle_zellen)
    last_cycle = DB.get_zell_cycle(zelle)
    last_cycle = last_cycle.values[0][0] if not last_cycle.empty else 1
    cycle = con2.number_input("Zyklus eingeben", min_value=0, max_value=1000, value=last_cycle, step=1)
    folder = con2.text_input("Daten-Ordner eingeben", value="/Volumes/ftm/EV_Lab_BatLab/02_Messexport/Urban/02_EIS/02_BioLogic/Sony US18650VTC5A/Charakterisierung/U_VTC5A_007", placeholder="/Data")

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
                st.session_state.filter_files.style.applymap(highlight_status, subset=["Status"]),
                key="data",
                on_select="rerun",
                selection_mode="multi-row",
            )
            selected_rows = st.session_state.filter_files.iloc[event.selection.rows]
            if con2.button("Analyse", type="primary", use_container_width=True, disabled=dis_button):
                try:
                    file_dir = [os.path.join(folder, f) for f in selected_rows["Datei"]]
                    with st.spinner("Analysieren...",show_time=True):
                        DA.analyze_data(file_path=file_dir, cycle=cycle, Zelle=zelle, save_data=True)
                        con2.success("Daten erfolgreich in Datenbank gespeichert.")
                        st.rerun()
                except Exception as e:
                    con2.error(f"Fehler beim Analysieren: {e}")
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
        DB.delete_file(files)


def delete_data_app():
    st.title("Daten löschen")
    DB = st.session_state["DB"]

    con1 = st.container(border=True)
    con1.header("Data Filtern")
    alle_zellen = DB.get_all_zells()
    zelle = con1.selectbox("Zellen eingeben", alle_zellen)
    all_cycles = DB.get_zell_cycle(zelle,Max=False)
    all_cycles = all_cycles.sort_values(by='Cycle').values

    cycle_sel = con1.multiselect(
        "Zyklus auswählen?",
        all_cycles,
    )

    if not cycle_sel:
        cycle = all_cycles.flatten().tolist()
    else:
        cycle = cycle_sel
    data = pd.DataFrame()
    for cyc in cycle:
        dat = DB.get_file(cyc, zelle)
        data = pd.concat([data, dat], ignore_index=True)
        st.session_state.filter_files = data

    event = con1.dataframe(
        st.session_state.filter_files,
        key="data",
        on_select="rerun",
        selection_mode="multi-row",
    )
    selected_rows = st.session_state.filter_files.iloc[event.selection.rows]

    if con1.button("Löschen", type="primary", use_container_width=True):
        file_loeschen(selected_rows["name"])