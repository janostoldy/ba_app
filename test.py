import pandas as pd
import numpy as np
import plotly.express as px

# Beispiel-Datenpunkte für ein CCCV-Ladeprofil
# x-Achse: Ladezeit (in h)
# y-Achse 1: Zellspannung (in V)
# y-Achse 2: Ladestrom (in C-Rate)

time = np.linspace(0, 3, 100)  # 0 bis 3 Stunden in 3-Minuten-Schritten

# Zellspannung (V): erst linearer Anstieg (CC-Phase), dann Plateau (CV-Phase)
voltage = np.piecewise(time,
                       [time < 1.7, time >= 1.7],
                       [lambda t: 0.5 + (t/1.7)*(1.5-0.7),  # Anstieg von 3.0V auf 4.2V
                        1.3])

# Ladestrom (C-Rate): konstant bis 1.5h, danach exponentiell abfallend
current = np.piecewise(time,
                       [time < 1.7, time >= 1.7],
                       [1.0, lambda t: np.exp(-(t-1.7)*2)])

# DataFrame erstellen
sp = pd.DataFrame({
    "Zeit_h": time,
    "values": voltage,
    "kind": "Spannung"
})
st = pd.DataFrame({
    "Zeit_h": time,
    "values": current,
    "kind": "Strom"
})
df = pd.concat([sp, st], ignore_index=True)

fig = px.line(df, x="Zeit_h", y="values",color="kind",)
fig.show()
