from typing import Any

from galvani import BioLogic
from datenbank import df_in_sqlite
from config import sql_spalten, mes_spalten
import pandas as pd

def analyze_data(file_path, cycle):

    for data_name in file_path:
        #print('Processing: ' + os.path.basename(data_name))
        mpr_file = BioLogic.MPRfile(data_name)
        df = pd.DataFrame(mpr_file.data)
        df = df.rename(columns=mes_spalten)

        # Eis Messung
        start_eis_indices = df[((df['flags'] == 37) | (df['flags'] == 165)) & (df['freqHz'] > 0)].index
        end_eis_indices = df[((df['flags'] == 69) | (df['flags'] == 197)) & (df['freqHz'] > 0)].index
        eis_values = [df.loc[start:end] for start, end in zip(start_eis_indices, end_eis_indices)]
        eis_soc = round(df.QQomAh[start_eis_indices - 1] / 125) * 125
        eis_ImA = df.ImA[start_eis_indices - 1]
        eis_Calc_ImA = round(eis_ImA / 1250) * 1250
        start_time = df.times[start_eis_indices]
        eis_str = [f"{cycle}/{soc}/{ima}" for soc, ima in zip(eis_soc, eis_Calc_ImA)]
        eis_str = [st.replace('.', '_') for st in eis_str]

        for i, eis in enumerate(eis_values):
            eis['SOC'] = eis_soc.iloc[i]
            eis['Calc_ImA'] = eis_Calc_ImA.iloc[i]
            eis['Cycle'] = cycle
            eis['calc_times'] = eis['times'] - start_time.iloc[i]
            eis['Messung'] = eis_str[i]
            eis['Type'] = 'Eis'

        # Deis Messung
        deis_values = df[((df['flags'] == 117) | (df['flags'] == 245)) & (df['freqHz'] > 0)]
        deis_indices = deis_values.index
        deis_soc = round(df.QQomAh[start_eis_indices - 1] / 125) * 125
        deis_ImA = df.ImA[deis_indices - 1]
        deis_Calc_ImA = round(deis_ImA / 1250) * 1250
        deis_str = [f"{cycle}/{soc}/{ima}" for soc, ima in zip(deis_soc, deis_Calc_ImA)]
        deis_str = [st.replace('.', '_') for st in deis_str]

        for i, deis in enumerate(deis_values):
            deis['SOC'] = deis_soc.iloc[i]
            deis['Calc_ImA'] = deis_Calc_ImA.iloc[i]
            deis['Cycle'] = cycle
            deis['calc_times'] = 0
            deis['Messung'] = deis_str[i]
            deis['Type'] = 'Deis'

        eis_sql = pd.DataFrame()
        for eis in eis_values:
            for spalte in sql_spalten:
                if spalte in eis.columns:
                    eis_sql[spalte] = eis_values[spalte]

        df_in_sqlite(deis_values, 'Eis_Analyse.db', 'Datapoints')






file_path = ['00_Test_Data/test.mpr']
cycle = 1
analyze_data(file_path, cycle)