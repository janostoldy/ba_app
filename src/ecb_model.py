import numpy as np
def model(x,f):
    L = x[0]
    Rs = (x[1] * 0.001)
    RSEI = x[2] * 0.001
    CSEI = x[3]
    Rct = x[4] * 0.001
    Cdl = x[5]
    alphaSEI = x[6]
    alphaCT = x[7]

    omega = 2 * np.pi * f
    ZL = 1j * omega * L * 0.000001
    Zcsei = 1 / (CSEI * (1j * omega) ** alphaSEI)
    Zsei = 1 / (1 / RSEI + 1 / Zcsei)
    Zcdl = 1 / (Cdl * (1j * omega) ** alphaCT)
    Zct = 1 / (1 / Rct + 1 / Zcdl)
    Z = ZL + Rs + Zsei + Zct
    y1 = Z.real
    y2 = Z.imag * -1
    return np.array([y1, y2])