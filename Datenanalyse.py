
import hashlib
from galvani import BioLogic
from config import sql_spalten, mes_spalten
import pandas as pd
import numpy as np

class EIS_Analyse:
    def __init__(self, datenbank):
        # Initialisiere die Datenbankverbindung
        self.DB = datenbank

    def create_hash(self, Messung, freqHz, cycle, soc, ima):
        # Erstelle einen Hash-Wert für die Zeile
        hash_input = f"{Messung}/{freqHz}/{cycle}/{soc}/{ima}"
        return hashlib.sha256(hash_input.encode()).hexdigest()

    def analyze_data(self, file_path, cycle):
        for data_name in file_path:
            #print('Processing: ' + os.path.basename(data_name))
            mpr_file = BioLogic.MPRfile(data_name)
            df = pd.DataFrame(mpr_file.data)
            df = df.rename(columns=mes_spalten)

            # Eis Messung
            start_eis_indices = df[((df['flags'] == 37) | (df['flags'] == 165)) & (df['freqHz'] > 0)].index
            end_eis_indices = df[((df['flags'] == 69) | (df['flags'] == 197)) & (df['freqHz'] > 0)].index
            eis_values = [df.loc[start:end].copy() for start, end in zip(start_eis_indices, end_eis_indices)]
            eis_soc = round(df.QQomAh[start_eis_indices - 1] / 125) * 125
            eis_ImA = df.ImA[start_eis_indices - 1]
            eis_Calc_ImA = round(eis_ImA / 1250) * 1250
            start_time = df.times[start_eis_indices]

            for i, eis in enumerate(eis_values):
                # Real und Imaginärteil berechnen
                eis_phi = np.deg2rad(eis['PhaseZdeg'])
                eis.loc[:,'calc_ReZOhm'] = eis['ZOhm'] * np.cos(eis_phi.values)
                eis.loc[:,'calc_ImZOhm'] = eis['ZOhm'] * np.sin(eis_phi.values)

                eis_hashes = [self.create_hash('EIS', freq, cycle, eis_soc.iloc[i], eis_Calc_ImA.iloc[i]) for freq in eis['freqHz']]
                eis.loc[:,'SOC'] = eis_soc.iloc[i]
                eis.loc[:,'Calc_ImA'] = eis_Calc_ImA.iloc[i]
                eis.loc[:,'Cycle'] = cycle
                eis.loc[:,'calc_times'] = eis['times'] - start_time.iloc[i]
                eis.loc[:,'hash'] = eis_hashes
                eis.loc[:,'Typ'] = 'Eis'
                eis.loc[:,'Datei'] = data_name

            # Deis Messung
            deis_values = df[((df['flags'] == 117) | (df['flags'] == 245)) & (df['freqHz'] > 0)].copy()
            deis_indices = deis_values.index
            deis_soc = round(df.QQomAh[deis_indices - 1] / 125) * 125
            deis_ImA = df.ImA[deis_indices - 1]
            deis_Calc_ImA = round(deis_ImA / 1250) * 1250
            deis_freq = deis_values['freqHz']
            deis_hashes = [self.create_hash('DEIS', freq, cycle, soc, ima) for soc, ima, freq in zip(deis_soc, deis_Calc_ImA, deis_freq)]

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
            deis_values.loc[:,'calc_times'] = 0
            deis_values.loc[:,'hash'] = deis_hashes
            deis_values.loc[:,'Typ'] = 'Deis'
            deis_values.loc[:, 'Datei'] = data_name

            self.insert_data(eis_values, deis_values, data_name)

    def insert_data(self, eis_values, deis_values, data_name):
        print('[Info] Insert Data from: ' + data_name)
        # Save Eis and Deis values to SQLite database
        for eis in eis_values:
            self.DB.df_in_sqlite(df=eis, table_name='Datapoints')
        self.DB.df_in_sqlite(df=deis_values, table_name='Datapoints')
