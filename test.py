from Classes.datenbank import Database
import pandas as pd

DB = Database("Impedanz")
files = DB.get_all_kapa()

files = pd.DataFrame(files)