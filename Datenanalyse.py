from galvani import BioLogic
from datenbank import df_in_sqlite, Spalten
import pandas as pd

def analyze_data(file_path, cycle):

    for data_name in file_path:
        #print('Processing: ' + os.path.basename(data_name))
        mpr_file = BioLogic.MPRfile(data_name)
        df = pd.DataFrame(mpr_file.data)
        start_eis_indices = df[((df['flags'] == 37) | (df['flags'] == 165)) & (df['freq/Hz'] > 0)].index
        end_eis_indices = df[((df['flags'] == 69) | (df['flags'] == 197)) & (df['freq/Hz'] > 0)].index
        eis_values = pd.concat([df.loc[start:end] for start, end in zip(start_eis_indices, end_eis_indices)])
        deis_values = df[((df['flags'] == 117) | (df['flags'] == 245)) & (df['freq/Hz'] > 0)]
        deis_indices = deis_values.index
        soc = round(df.(Q-Qo)/mA[start_eis_indices - 1] / 125) * 125
        ImA = df.ImA[start_eis_indices - 1]
        Calc_ImA = round(ImA / 1250) * 1250
        Plot = {
            'QAh': soc,
            'Calc_ImA': Calc_ImA,
            'Cycle': cycle
        }

        eis_sql = pd.DataFrame()
        for spalte in Spalten:
            if spalte in eis_values.columns:
                eis_sql[spalte] = eis_values[spalte]
            else:
                eis_sql[spalte] = 0  # fehlende Spalten mit 0 füllen

        df_in_sqlite(deis_values, 'Eis_Analyse.db', 'Datapoints')






file_path = ['00_Test_Data/test.mpr']
cycle = 1
analyze_data(file_path, cycle)