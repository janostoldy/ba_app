import os
import hashlib
from galvani import BioLogic
from config import sql_spalten, mes_spalten
import pandas as pd
import numpy as np
from scipy.signal import savgol_filter, find_peaks

class EIS_Analyse:
    def __init__(self, datenbank):
        # Initialisiere die Datenbankverbindung
        self.DB = datenbank

    def create_hash(self, Messung, freqHz, cycle, soc, ima, zelle):
        # Erstelle einen Hash-Wert für die Zeile
        hash_input = f"{Messung}{freqHz}{cycle}{soc}{ima}{zelle}"
        return hashlib.sha256(hash_input.encode()).hexdigest()

    def calc_niquist_data(self, eis_data,save_data):
        results = []
        for eis in eis_data:
            re = eis['calc_ReZOhm']
            im = eis['calc_ImZOhm']
            freq = eis['freqHz']
            s_im = savgol_filter(im, window_length=7, polyorder=2)
            minima_indices, _ = find_peaks(-s_im)
            minima_indices = minima_indices[0]
            maxima_indices, _ = find_peaks(s_im)
            maxima_indices = maxima_indices[0]
            temp = {
                'hash': eis['hash'].values[0],
                'QAh': eis['SOC'].values[0],
                'Calc_ImA': eis['Calc_ImA'].values[0],
                'Zyklus': eis['Cycle'].values[0],
                'Im_Min': im.iloc[minima_indices],
                'Re_Min': re.iloc[minima_indices],
                'freq_Min': freq.iloc[minima_indices],
                'Im_Max': im.iloc[maxima_indices],
                'Re_Max': re.iloc[maxima_indices],
                'freq_Max': freq.iloc[maxima_indices]
            }
            results.append(temp)
        
        niquist_df = pd.DataFrame(results)
        if save_data:
            self.DB.df_in_DB(df=niquist_df, table_name='Niquist')

    def analyze_data(self, file_path, cycle, Zelle, save_data):
        import streamlit as st
        for data_name in file_path:
            #print('Processing: ' + os.path.basename(data_name))
            mpr_file = BioLogic.MPRfile(data_name)
            df = pd.DataFrame(mpr_file.data)
            df = df.rename(columns=mes_spalten)

            if 'ZOhm' not in df.columns:
                cycle_index = df[((df['flags'] == 39) | (df['flags'] == 167))]
                cycle = cycle + len(cycle_index)
                continue

            # Eis Messung
            st.write(df)

            start_eis_indices = df[((df['flags'] == 37) | (df['flags'] == 165)) & (df['freqHz'] > 0)].index
            start_eis_indices = df[((df['flags'] == 39) | (df['flags'] == 181)) & (df['freqHz'] > 0)].index
            end_eis_indices = df[((df['flags'] == 69) | (df['flags'] == 197)) & (df['freqHz'] > 0)].index
            end_eis_indices = df[((df['flags'] == 85) | (df['flags'] == 213)) & (df['freqHz'] > 0)].index
            if len(start_eis_indices) == 0 | len(end_eis_indices) == 0:
                raise Exception('No EIS data found in file or wrong flags.')
            eis_values = [df.loc[start:end].copy() for start, end in zip(start_eis_indices, end_eis_indices)]
            eis_soc = round(df.QQomAh[start_eis_indices - 1] / 125) * 125
            eis_ImA = df.ImA[start_eis_indices - 1]
            eis_Calc_ImA = round(eis_ImA / 1250) * 1250
            start_time = df.times[start_eis_indices]

            for i, eis in enumerate(eis_values):
                # Real und Imaginärteil berechnen
                eis_phi = np.deg2rad(eis['PhaseZdeg'])
                eis.loc[:,'calc_ReZOhm'] = eis['ZOhm'] * np.cos(eis_phi.values)
                eis.loc[:,'calc_ImZOhm'] = eis['ZOhm'] * np.sin(eis_phi.values) *-1

                eis_hashes = [self.create_hash('EIS', freq, cycle, eis_soc.iloc[i], eis_Calc_ImA.iloc[i], Zelle) for freq in eis['freqHz']]
                eis.loc[:,'SOC'] = eis_soc.iloc[i]
                eis.loc[:,'Calc_ImA'] = eis_Calc_ImA.iloc[i]
                eis.loc[:,'Cycle'] = cycle
                eis.loc[:,'Zelle'] = Zelle
                eis.loc[:,'calc_times'] = eis['times'] - start_time.iloc[i]
                eis.loc[:,'hash'] = eis_hashes
                eis.loc[:,'Typ'] = 'Eis'
                eis.loc[:,'Datei'] = os.path.basename(data_name)
            self.calc_niquist_data(eis_values,save_data)

            # Deis Messung
            deis_values = df[((df['flags'] == 117) | (df['flags'] == 245)) & (df['freqHz'] > 0)].copy()
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
            deis_values.loc[:,'calc_ReZOhm'] = deis_values['ZOhm'] * np.cos(deis_phi)
            deis_values.loc[:,'calc_ImZOhm'] = deis_values['ZOhm'] * np.sin(deis_phi)

            deis_values.loc[:,'SOC'] = deis_soc
            deis_values.loc[:,'Calc_ImA'] = deis_Calc_ImA
            deis_values.loc[:,'Cycle'] = cycle
            deis_values.loc[:,'Zelle'] = Zelle
            deis_values.loc[:,'calc_times'] = 0
            deis_values.loc[:,'hash'] = deis_hashes
            deis_values.loc[:,'Typ'] = 'Deis'
            deis_values.loc[:, 'Datei'] = os.path.basename(data_name)

            if save_data:
                self.insert_data(eis_values, deis_values, data_name)
        return cycle

    def insert_data(self, eis_values, deis_values, data_name):
        for eis in eis_values:
            self.DB.df_in_DB(df=eis, table_name='Datapoints')
        self.DB.df_in_DB(df=deis_values, table_name='Datapoints')
