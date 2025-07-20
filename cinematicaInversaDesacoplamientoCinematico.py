import numpy as np
from math import atan2, sqrt, cos, sin

# Parámetros del robot
L1, L2, L3 = 0.5, 1.0, 0.8
px, py, pz = 1.2, 0.5, 0.7

# --- Cinemática inversa de posición ---
theta1 = atan2(py, px)
r = sqrt(px**2 + py**2)
h = pz - L1
D = (r**2 + h**2 - L2**2 - L3**2) / (2 * L2 * L3)
theta3 = atan2(sqrt(1 - D**2), D)  # Codo arriba
theta2 = atan2(h, r) - atan2(L3 * sin(theta3), L2 + L3 * cos(theta3))

# --- Cinemática inversa de orientación (simplificada) ---
# (Asumimos rotación en Z de 30°)
theta4 = 0.0
theta5 = np.radians(30.0)
theta6 = 0.0

print(f"θ1 = {np.degrees(theta1):.1f}°")
print(f"θ2 = {np.degrees(theta2):.1f}°, θ3 = {np.degrees(theta3):.1f}°")
print(f"θ4 = {np.degrees(theta4):.1f}°, θ5 = {np.degrees(theta5):.1f}°, θ6 = {np.degrees(theta6):.1f}°")