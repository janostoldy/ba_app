import numpy as np
from scipy.optimize import minimize
from src.ecb_model import model

y_target = np.array([
    (0.022204105, -0.0036374244),
    (0.022330858, -0.0024087776),
    (0.022501128, -0.0014602159),
    (0.022750054, -0.0005602917),
    (0.023047494, 0.00015872692),
    (0.023371506, 0.0007677276),
    (0.023733163, 0.0012870621),
    (0.024157366, 0.0017347448),
    (0.024595903, 0.0021161784),
    (0.02507345, 0.0024471092),
    (0.025575442, 0.0027058283),
    (0.026113631, 0.0029302738),
    (0.026608145, 0.003067933),
    (0.027204614, 0.003177767),
    (0.0277953, 0.0032591254),
    (0.028350592, 0.0032628346),
    (0.028890835, 0.003241284),
    (0.029454397, 0.0031949745),
    (0.030003887, 0.0031070109),
    (0.030500202, 0.0029603294),
    (0.03095579, 0.0027937056),
    (0.03138186, 0.0026007209),
    (0.031736422, 0.0024175006),
    (0.032038055, 0.0022366075),
    (0.032318246, 0.002061167),
    (0.032547534, 0.0019469531),
])

def opjective(x):
    frequencies = np.logspace(np.log10(5), np.log10(1600), num=26)
    frequencies = np.array(frequencies, dtype=float)
    y = model(x,frequencies)
    return np.sum((y -y_target.T)**2)

frequencies = np.logspace(np.log10(5), np.log10(1600), num=26)
frequencies = np.array(frequencies, dtype=float)
x0 = np.ones(8)*0.001
bnds = [(0, 1000)] * 8
res = minimize(opjective, x0, bounds=bnds, method="L-BFGS-B", options={"maxiter":1000})
print("Optimale Inputs:", res.x)
print("Erreichte Outputs:", model(res.x,frequencies))
print("Zielfunktionswert:", res.fun)