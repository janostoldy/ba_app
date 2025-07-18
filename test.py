import pandas as pd
from config import mes_spalten
from galvani import BioLogic

mpr_file = BioLogic.MPRfile("/Volumes/ftm/EV_Lab_BatLab/02_Messexport/Urban/BA_Toldy/Charakterisierung/JT_VTC_001/JT_VTC_001_Characterization_02_MB_CA1.mpr")
df = pd.DataFrame(mpr_file.data)
dva_raw = df.rename(columns=mes_spalten)

print(dva_raw.head)