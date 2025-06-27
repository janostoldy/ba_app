import os
import hashlib
from galvani import BioLogic
from config import sql_spalten, mes_spalten
import pandas as pd
import numpy as np
from scipy.signal import savgol_filter, find_peaks
from scipy.ndimage import gaussian_filter1d

class Analyse:
    def __init__(self, datenbank):
        # Initialisiere die Datenbankverbindung
        self.DB = datenbank

    def analyse_eingang(self, file_path, cycle, Zelle, save_data, bar):
        for data_path in file_path:
            data_name = os.path.basename(data_path)
            data_path = [data_path]
            if "01_MB" in data_name:
                bar.progress(1 / 3, text="Kapazität analysieren...")
                self.analys_kapa_data(data_path, cycle, Zelle, save_data)
            elif "02_MB" in data_name:
                bar.progress(2 / 3, text="OCV analysieren...")
                self.analys_OCV_data(data_path, cycle, Zelle, save_data)
            elif "03_MB" in data_name:
                bar.progress(3 / 3, text="EIS analysieren...")
                self.analyze_EIS_data(data_path, cycle, Zelle, save_data)
            else:
                raise Exception("Keine Eingangsprüfung!")


    def create_hash(self, Messung, freqHz, cycle, soc, ima, zelle):
        # Erstelle einen Hash-Wert für die Zeile
        hash_input = f"{Messung}{freqHz}{cycle}{soc}{ima}{zelle}"
        return hashlib.sha256(hash_input.encode()).hexdigest()

    def add_relax(self, file_path, cycle, Zelle, save_data):
        try:
            for data_path in file_path:
                data_name = os.path.basename(data_path)
                if save_data:
                    self.DB.insert_file(data_name, cycle, "Thermische-Relaxation", Zelle, "Relaxation")
        except Exception as e:
            raise Exception(f"Fehler bei Relaxation -> {e}")

    def analyze_Aeging(self, file_path, cycle, Zelle, save_data, bar):
        try:
            n_files = len(file_path)
            for i, data_path in enumerate(file_path):
                data_name = os.path.basename(data_path)
                bar.progress((i+1)/n_files, text=f"Analysieren von Datei {i+1} von {n_files}: {data_name}")
                mpr_file = BioLogic.MPRfile(data_path)
                df = pd.DataFrame(mpr_file.data)
                ageing_raw = df.rename(columns=mes_spalten)
                if 'ZOhm' in ageing_raw:
                    self.analyze_EIS_data([data_path], cycle, Zelle, save_data)
                    continue
                aeging_cycles = ageing_raw['cycle number'].iloc[-1] - ageing_raw['cycle number'].iloc[0]
                cycle = cycle + aeging_cycles
                if save_data:
                    self.DB.update_zelle(Zelle, cycle)
                    self.DB.insert_file(data_name, cycle, "Aeging-Analyse", Zelle, "Ageing")
        except Exception as e:
            raise Exception(f"Fehler bei Ageing-Analyse -> {e}")

    def calc_niquist_data(self, eis_data,save_data):
        results = []
        for eis in eis_data:
            eis = eis[eis["freqHz"] != 1999]
            eis = eis.sort_values(by="freqHz")
            re = eis['calc_ReZOhm']
            im = eis['calc_ImZOhm']
            freq = eis['freqHz']
            s_im = savgol_filter(im, window_length=7, polyorder=2)
            minima_indices, _ = find_peaks(-s_im)
            minima_indices = minima_indices[0]
            maxima_indices, _ = find_peaks(s_im)
            maxima_indices = maxima_indices[0]
            zif_indizes = np.where(np.diff(np.sign(im)))[0]
            zif_indizes = zif_indizes[0]

            temp = {
                'SoC': eis['SoC'].values[0],
                'Calc_ImA': eis['Calc_ImA'].values[0],
                'Im_Min': im.iloc[minima_indices],
                'Re_Min': re.iloc[minima_indices],
                'freq_Min': freq.iloc[minima_indices],
                'Im_Max': im.iloc[maxima_indices],
                'Re_Max': re.iloc[maxima_indices],
                'freq_Max': freq.iloc[maxima_indices],
                'Im_ZIF': im.iloc[zif_indizes],
                'Re_ZIF': re.iloc[zif_indizes],
                'freq_ZIF': freq.iloc[zif_indizes],
                'Datei': eis['Datei'].values[0]
            }
            results.append(temp)
        
        niquist_df = pd.DataFrame(results)
        if save_data:
            self.DB.df_in_DB(df=niquist_df, table_name='EIS_Points')

    def analyze_EIS_data(self, file_path, cycle, Zelle, save_data):
        try:
            for data_path in file_path:
                data_name = os.path.basename(data_path)
                mpr_file = BioLogic.MPRfile(data_path)
                df = pd.DataFrame(mpr_file.data)
                df = df.rename(columns=mes_spalten)

                if 'ZOhm' not in df.columns:
                    raise Exception("Keine Eis-Daten")

                # Eis Messung
                start_eis_indices = df[((df['flags'] == 37) | (df['flags'] == 165)) & (df['freqHz'] > 0)].index
                end_eis_indices = df[((df['flags'] == 69) | (df['flags'] == 197)) & (df['freqHz'] > 0)].index
                if len(start_eis_indices) == 0 or len(end_eis_indices) == 0:
                    start_eis_indices = df[((df['flags'] == 53) | (df['flags'] == 181)) & (df['freqHz'] > 0)].index
                    end_eis_indices = df[((df['flags'] == 85) | (df['flags'] == 213)) & (df['freqHz'] > 0)].index
                if len(start_eis_indices) == 0 or len(end_eis_indices) == 0:
                    raise Exception('No EIS data found in file or wrong flags.')

                eis_values = [df.loc[start:end].copy() for start, end in zip(start_eis_indices, end_eis_indices)]
                zero_soc = min(df.QQomAh)
                eis_soc = round((df.QQomAh[start_eis_indices - 1] - zero_soc) / 125) * 125
                eis_ImA = df.ImA[start_eis_indices - 1]
                eis_Calc_ImA = round(eis_ImA / 1250) * 1250
                start_time = df.times[start_eis_indices]

                for i, eis in enumerate(eis_values):
                    # Real und Imaginärteil berechnen
                    eis_phi = np.deg2rad(eis['PhaseZdeg'])
                    eis.loc[:, 'calc_ReZOhm'] = eis['ZOhm'] * np.cos(eis_phi.values)
                    eis.loc[:, 'calc_ImZOhm'] = eis['ZOhm'] * np.sin(eis_phi.values) * -1

                    eis_hashes = [self.create_hash('EIS', freq, cycle, eis_soc.iloc[i], eis_Calc_ImA.iloc[i], Zelle) for freq in eis['freqHz']]
                    eis.loc[:, 'SoC'] = eis_soc.iloc[i]
                    eis.loc[:, 'Calc_ImA'] = eis_Calc_ImA.iloc[i]
                    eis.loc[:, 'Cycle'] = cycle
                    eis.loc[:, 'Zelle'] = Zelle
                    eis.loc[:, 'calc_times'] = eis['times'] - start_time.iloc[i]
                    eis.loc[:, 'hash'] = eis_hashes
                    eis.loc[:, 'Typ'] = 'Eis'
                    eis.loc[:, 'Datei'] = data_name

                self.calc_niquist_data(eis_values, save_data)
                if save_data:
                    self.DB.insert_file(data_name, cycle, "Eis Messung", Zelle, "EIS")
                    for eis in eis_values:
                        self.DB.df_in_DB(df=eis, table_name='EIS')

        except Exception as e:
            raise Exception(f"Fehler bei EIS-Analyse -> {e}")

    def analyze_DEIS_data(self, df, data_name, cycle, Zelle, save_data, eis_values):
        try:
            deis_values = df[((df['flags'] == 117) | (df['flags'] == 245)) & (df['freqHz'] > 0)].copy()
            if len(deis_values) == 0:
                deis_values = df[((df['flags'] == 101) | (df['flags'] == 229)) & (df['freqHz'] > 0)].copy()
            if len(deis_values) == 0:
                raise Exception('No DEIS data found in file or wrong flags.')
            deis_indices = deis_values.index
            deis_soc = round(df.QQomAh[deis_indices - 1] / 125) * 125
            deis_ImA = df.ImA[deis_indices - 1]
            deis_Calc_ImA = round(deis_ImA / 1250) * 1250
            deis_freq = deis_values['freqHz']
            deis_hashes = [self.create_hash('DEIS', freq, cycle, soc, ima, Zelle) for soc, ima, freq in zip(deis_soc, deis_Calc_ImA, deis_freq)]

            #Anpassungen, um Daten zusammenzufügen
            deis_soc.index = deis_soc.index + 1
            deis_Calc_ImA.index = deis_Calc_ImA.index + 1

            # Real und Imaginärteil berechnen
            deis_phi = np.deg2rad(deis_values['PhaseZdeg'])  # Konvertiere Winkel in Radiant
            deis_values.loc[:, 'calc_ReZOhm'] = deis_values['ZOhm'] * np.cos(deis_phi)
            deis_values.loc[:, 'calc_ImZOhm'] = deis_values['ZOhm'] * np.sin(deis_phi)

            deis_values.loc[:, 'SoC'] = deis_soc
            deis_values.loc[:, 'Calc_ImA'] = deis_Calc_ImA
            deis_values.loc[:, 'Cycle'] = cycle
            deis_values.loc[:, 'Zelle'] = Zelle
            deis_values.loc[:, 'calc_times'] = 0
            deis_values.loc[:, 'hash'] = deis_hashes
            deis_values.loc[:, 'Typ'] = 'Deis'
            deis_values.loc[:, 'Datei'] = os.path.basename(data_name)

            if save_data:
                self.DB.df_in_DB(df=deis_values, table_name='EIS')
        except Exception as e:
            raise Exception(f"Fehler bei DEIS-Analyse -> {e}")

    def analys_kapa_data(self,file_path, cycle, Zelle, save_data):
        try:
            for data_path in file_path:
                data_name = os.path.basename(data_path)
                mpr_file = BioLogic.MPRfile(data_path)
                df = pd.DataFrame(mpr_file.data)
                kapa_raw = df.rename(columns=mes_spalten)
                kapa = max(kapa_raw['QQomAh']) - min(kapa_raw['QQomAh'])

                data = pd.DataFrame({
                    'Datei': [data_name],
                    'Info': [f"Zelle {Zelle} nach Zyklus {cycle}"],
                    'Kapa': [kapa],
                })

                if save_data:
                    self.DB.df_in_DB(df=data, table_name='Kapa')
                    self.DB.insert_file(data_name, cycle, "Kapazitäts-Analyse", Zelle, "Kapa")
        except Exception as e:
            raise Exception(f"Fehler bei Kapazitäts-Analyse -> {e}")

    def analys_OCV_data(self, file_path, cycle, Zelle, save_data):
        try:
            for data_path in file_path:
                data_name = os.path.basename(data_path)
                mpr_file = BioLogic.MPRfile(data_path)
                df = pd.DataFrame(mpr_file.data)
                dva_raw = df.rename(columns=mes_spalten)

                QQomAh_smoove = gaussian_filter1d(dva_raw["QQomAh"], sigma=5)
                QQomAh_diff = np.gradient(QQomAh_smoove)
                Ecell_smoove = gaussian_filter1d(dva_raw["EcellV"], sigma=5)
                Ecell_diff = np.gradient(Ecell_smoove)
                dva = Ecell_diff[:] / QQomAh_diff[:]
                dva_smoove = gaussian_filter1d(dva, sigma=15)
                dva_ind = np.where(dva_smoove < 0.001)
                first_index = dva_ind[0][0]
                dva_ind = np.where(np.diff(dva_smoove) > 0)[0]
                last_index = dva_ind[-1] + 1 if len(dva_ind) > 0 else len(dva_smoove) - 1

                dva_edit = dva_raw[first_index:last_index]
                dva_edit['QQomAh_smoove'] = QQomAh_smoove[first_index:last_index]
                dva_edit['EcellV_smoove'] = Ecell_smoove[first_index:last_index]
                dva_edit['calc_dV_dQ'] = dva_smoove[first_index:last_index]
                dva_edit['cycle'] = cycle
                dva_edit['Zelle'] = Zelle
                dva_edit['Datei'] = data_name

                Q0_val = QQomAh_smoove[0]
                Q0 = dva_edit['QQomAh_smoove'].iloc[0]
                Qactual = dva_edit['QQomAh_smoove'].iloc[-1]
                peaks = find_peaks(dva_edit['calc_dV_dQ'].values, distance=700, height=0.00035)[0]
                Q1 = dva_edit['QQomAh_smoove'].iloc[peaks[-2]]
                Q2 = Qactual - Q1
                Q3 = Qactual - dva_edit['QQomAh_smoove'].iloc[peaks[-1]]

                calc_Points = pd.DataFrame({
                    'Datei': [data_name] * 5,
                    'Point': ['Q0', 'Q1', 'Q2', 'Q3', 'Qactual'],
                    'Value': [Q0_val, Q1, Q2, Q3, Qactual],
                    'X_Start': [Q0, Q0, Qactual - Q2, Qactual - Q3, Q0],
                    'X_End': [Q0, Q1, Qactual, Qactual, Qactual],
                })

                if save_data:
                    self.DB.df_in_DB(df=dva_edit, table_name='DVA')
                    self.DB.df_in_DB(df=calc_Points, table_name='DVA_Points')
                    self.DB.insert_file(data_name, cycle, "DVA Analyse", Zelle, "DVA")
        except Exception as e:
            raise Exception(f"Fehler bei OCV-Analyse -> {e}")

    def insert_data(self, eis_values, deis_values, data_name):
        for eis in eis_values:
            self.DB.df_in_DB(df=eis, table_name='EIS')
        self.DB.df_in_DB(df=deis_values, table_name='EIS')
