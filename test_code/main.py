from classes.datenbank import Database
from classes.datenanalyse import EIS_Analyse

try:
    DB = Database()
    DA = EIS_Analyse(DB)

    print('[Info] Open Connection')
    DB.create_table()
    file_path = ['00_Test_Data/test.mpr']
    cycle = 1
    Zelle = "SN0001"
    DA.analyze_data(file_path, cycle, Zelle, True)
    print('[Info] Done')

finally:
    try:

        print('[Info] Closed Connection')
    except Exception as e:
        print(f'[Error] Failed to close connection: {e}')