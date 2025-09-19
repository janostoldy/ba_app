import numpy as np

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