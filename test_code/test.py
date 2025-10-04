import numpy as np
from scipy.optimize import curve_fit
import plotly.express as px
import plotly.graph_objects as go

# Beispielwerte
x = np.array([25, 30, 40])
y = np.array([-4.972367, -1.8538499, 1.795783])

def exp_func(x, a, b):
    return a * np.log(b * x)

params, _ = curve_fit(exp_func, x, y,p0=(26, -4))
a, b = params
print(a, b)
x_fit = np.linspace(min(x), max(x), 100)
y_fit = exp_func(x_fit, a, b)

fig = px.scatter(x=x, y=y, title="calc_times")
fig.add_trace(go.Scatter(
    x=x_fit,
    y=y_fit,
    mode='lines',
    name='Exponentieller Fit',
    line=dict(color='blue')
))
fig.show()