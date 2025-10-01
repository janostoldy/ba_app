import numpy as np
import streamlit as st

def mean_pairwise_abs_diff(x):
    x = np.asarray(x)
    x = x[~np.isnan(x)]         # NaNs entfernen falls nötig
    n = x.size
    if n < 2:
        return 0.0
    x_sorted = np.sort(x)       # O(n log n)
    k = np.arange(1, n+1)       # 1..n
    S = (x_sorted * (2*k - n - 1)).sum()
    mean = 2.0 * S / (n * (n - 1))
    return mean

# Funktion zur Berechnung der relativen Abweichung zum Median
def max_dev_to_median(x):
    med = np.median(x)
    return max(np.abs(x - med) / med)

def robust_start_end_median(df):
    med_start = df.iloc[0]
    med_end = df.iloc[-3:].median()
    delta_abs = med_end - med_start
    delta_rel = abs(delta_abs / med_start)
    return delta_rel

def robust_start_end_abw(df, tol=0.05):
    werte = df["wert"]
    med_end = werte.iloc[-3:].median()
    for z, wert in enumerate(werte.values):
        delta_abs = abs((wert - med_end)/ med_end)
        if delta_abs < tol:
            return df['cycle'].iloc[z]
    return -1

def normiere_kurve(gruppe):
    last3 = gruppe.tail(3)['wert']
    median = last3.median()
    gruppe = gruppe.copy()
    gruppe['wert_norm'] = gruppe['wert'] / median if median != 0 else gruppe['wert']
    return gruppe