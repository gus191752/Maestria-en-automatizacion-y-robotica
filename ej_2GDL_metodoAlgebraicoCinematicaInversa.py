import numpy as np
from math import cos, sin, atan2, sqrt

# Parámetros del robot
L1, L2 = 1.0, 0.8
px, py = 1.2, 0.5

# Solución para theta2
cos_theta2 = (px**2 + py**2 - L1**2 - L2**2) / (2 * L1 * L2)
theta2 = atan2(sqrt(1 - cos_theta2**2), cos_theta2)  # Codo arriba
# theta2 = atan2(-sqrt(1 - cos_theta2**2), cos_theta2)  # Codo abajo

# Solución para theta1
theta1 = atan2(py, px) - atan2(L2 * sin(theta2), L1 + L2 * cos(theta2))

print(f"θ1 = {np.degrees(theta1):.2f}°, θ2 = {np.degrees(theta2):.2f}°")