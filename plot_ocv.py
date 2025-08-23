
from galvani import BioLogic
from config import mes_spalten
import pandas as pd
import numpy as np
from scipy.signal import savgol_filter, find_peaks
from scipy.ndimage import gaussian_filter1d
import plotly.express as px

# Optional für TikZ/PGFPlots export
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("pgf")
plt.rcParams.update({
    "pgf.texsystem": "pdflatex",
    "font.family": "sans-serif",
    "text.usetex": True,
    "pgf.rcfonts": False,
})

data_path = '00_Test_Data/OCV_plot.mpr'
mpr_file = BioLogic.MPRfile(data_path)
df = pd.DataFrame(mpr_file.data)
dva_raw = df.rename(columns=mes_spalten)
QQomAh_smoove = gaussian_filter1d(dva_raw["qqomah"], sigma=5)
Ecell_smoove = gaussian_filter1d(dva_raw["ecellv"], sigma=5)

plot_data = pd.DataFrame({
    "qqomah": QQomAh_smoove,
    "ecellv": Ecell_smoove
})

# Plot erstellen
fig, ax = plt.subplots(figsize=(10,5))
ax.plot(QQomAh_smoove, Ecell_smoove, color="#e37222")
ax.set_xlim(-100, 2500)
ax.set_xlabel("Kapazität [mAh]")
ax.set_ylabel("Zellspannung [V]")
ax.grid(True, which='both', color='#e0e0e0', linewidth=1)

# Plot als TikZ/PGFPlots speichern
plt.tight_layout()
plt.savefig("ocv_plot.pdf")