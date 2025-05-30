from galvani import BioLogic
import pandas as pd
import plotly.graph_objects as go


mpr_file = BioLogic.MPRfile("00_Test_Data/test_cycle.mpr")
df = pd.DataFrame(mpr_file.data)

fig = go.Figure()
fig.add_trace(go.Scatter(x=df['time/s'], y=df['flags'], mode='lines', name='flags'))
fig.add_trace(go.Scatter(x=df['time/s'], y=df['(Q-Qo)/mA.h'], mode='lines', name='(Q-Qo)/mA.h'))
fig.update_layout(title='flags und Q-Qo über der Zeit', xaxis_title='Zeit (s)', yaxis_title='Wert')
fig.show()

print(df)