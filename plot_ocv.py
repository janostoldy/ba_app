
from galvani import BioLogic
from config import mes_spalten
import pandas as pd
import numpy as np
from scipy.signal import savgol_filter, find_peaks
from scipy.ndimage import gaussian_filter1d
import plotly.express as px

data_path = '00_Test_Data/Kapa_Mes.mpr'
mpr_file = BioLogic.MPRfile(data_path)
df = pd.DataFrame(mpr_file.data)
dva_raw = df.rename(columns=mes_spalten)
indx_first = dva_raw.index[dva_raw["ima"] != 0.0][0]
indx_last = dva_raw.index[dva_raw["ima"] < 0.0][0]
dva_cut = dva_raw[indx_first:indx_last]
QQomAh_smoove = gaussian_filter1d(dva_cut["qqomah"], sigma=5)
Ecell_smoove = gaussian_filter1d(dva_cut["ecellv"], sigma=5)
plot_data = pd.DataFrame({
    "qqomah": QQomAh_smoove,
    "ecellv": Ecell_smoove,
    "ima": dva_cut["ima"],
    "times": dva_cut["times"],
})

# Prüfen, wie viele Zeilen vorhanden sind
rows = len(plot_data)
print(f"Originale Zeilen: {rows}")

# Wenn mehr als 2000 Zeilen: gleichmäßig sampeln
if rows > 2000:
    step = rows // 1000  # Schrittweite
    df_reduced = plot_data.iloc[::step, :].head(1000)  # gleichmäßig verteilen
else:
    df_reduced = plot_data.copy()
    print("Datei hat weniger als 2000 Zeilen, keine Reduktion nötig.")

# Neue CSV speichern
df_reduced.to_csv("Kapa.csv", index=False)
print(f"Reduzierte Datei gespeichert: Kapa.csv")