import pandas as pd
import plotly.graph_objects as go

soc = [
    "1.0–0.9", "0.9–0.8", "0.8–0.7", "0.7–0.6", "0.6–0.5",
    "0.5–0.4", "0.4–0.3", "0.3–0.2", "0.2–0.1", "0.1–0.0"
]

# Temperaturanstieg in °C/s (geschätzt aus dem Plot, y-Werte)
nmc = [0.010, 0.009, 0.009, 0.0095, 0.0095, 0.0105, 0.012, 0.014, 0.019, 0.028]
nca = [0.005, 0.006, 0.0047, 0.0048, 0.0052, 0.0085, 0.008, 0.01, 0.013, 0.023]
lfp = [0.0048, 0.0045, 0.0045, 0.0045, 0.0047, 0.0058, 0.0065, 0.0075, 0.010, 0.020]

fig = go.Figure()

fig.add_trace(go.Scatter(x=soc, y=nmc, mode='markers', name='NMC', line=dict(color='black')))
fig.add_trace(go.Scatter(x=soc, y=nca, mode='markers', name='NCA', line=dict(color='orange')))
fig.add_trace(go.Scatter(x=soc, y=lfp, mode='markers', name='LFP', line=dict(color='red')))

# Layout anpassen
fig.update_layout(
    title="Temperaturanstieg in Abhängigkeit vom SOC",
    xaxis_title="SOC",
    yaxis_title="Temperaturanstieg (°C/s)",
    template="simple_white",
    legend_title="Zellchemie"
)

# Plot anzeigen
fig.show()