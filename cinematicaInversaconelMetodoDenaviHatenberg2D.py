import numpy as np
import matplotlib.pyplot as plt
from math import cos, sin, atan2, sqrt, pi

# =============================================
# 1. Definición de parámetros D-H (robot RRR planar)
# =============================================
# Eslabón | theta (θ) | d | a | alpha (α)
dh_params = [
    {'theta': 0, 'd': 0, 'a': 0.5, 'alpha': 0},   # Eslabón 1
    {'theta': 0, 'd': 0, 'a': 0.8, 'alpha': 0},   # Eslabón 2
    {'theta': 0, 'd': 0, 'a': 0.6, 'alpha': 0}    # Eslabón 3
]

# =============================================
# 2. Función para calcular matriz de transformación A_i
# =============================================
def dh_matrix(theta, d, a, alpha):
    """Genera la matriz de transformación homogénea A_i para los parámetros D-H dados."""
    A = np.array([
        [cos(theta),  -sin(theta)*cos(alpha),  sin(theta)*sin(alpha), a*cos(theta)],
        [sin(theta),  cos(theta)*cos(alpha),  -cos(theta)*sin(alpha), a*sin(theta)],
        [0,                  sin(alpha),              cos(alpha),          d      ],
        [0,                       0,                       0,              1      ]
    ])
    return A

# =============================================
# 3. Cinemática directa (para verificación)
# =============================================
def forward_kinematics(theta1, theta2, theta3):
    """Calcula la posición del efector final dados los ángulos."""
    A1 = dh_matrix(theta1, dh_params[0]['d'], dh_params[0]['a'], dh_params[0]['alpha'])
    A2 = dh_matrix(theta2, dh_params[1]['d'], dh_params[1]['a'], dh_params[1]['alpha'])
    A3 = dh_matrix(theta3, dh_params[2]['d'], dh_params[2]['a'], dh_params[2]['alpha'])
    T = A1 @ A2 @ A3
    return T[:3, 3]  # Retorna [px, py, pz]

# =============================================
# 4. Cinemática inversa (Método algebraico-geométrico)
# =============================================
def inverse_kinematics(px, py):
    """Calcula theta1, theta2, theta3 para alcanzar (px, py)."""
    L1, L2, L3 = dh_params[0]['a'], dh_params[1]['a'], dh_params[2]['a']
    
    # Solución para theta1 (2 configuraciones posibles)
    theta1 = atan2(py, px)
    
    # Solución para theta2 y theta3 (ley de cosenos)
    r = sqrt(px**2 + py**2)
    D = (r**2 - L1**2 - L2**2) / (2 * L1 * L2)

    try:
        theta2 = atan2(sqrt(1 - D**2), D)  # Codo arriba
    except ValueError:
        pass
    
    # theta2 = atan2(-sqrt(1 - D**2), D)  # Codo abajo (configuración alternativa)
    
    # Solución para theta3
    
    try:
        theta3 = atan2(py - L1*sin(theta1), px - L1*cos(theta1)) - theta2
    except:
        pass


    return theta1, theta2, theta3

# =============================================
# 5. Ejemplo de uso y visualización
# =============================================
# Posición deseada del efector final
px_deseado = 0.5
py_deseado = 0.6

# Resolver cinemática inversa
theta1, theta2, theta3 = inverse_kinematics(px_deseado, py_deseado)
print(f"Soluciones encontradas:")
print(f"θ1 = {np.degrees(theta1):.2f}°")
print(f"θ2 = {np.degrees(theta2):.2f}°")
print(f"θ3 = {np.degrees(theta3):.2f}°")

# Verificar con cinemática directa
pos_efector = forward_kinematics(theta1, theta2, theta3)
print(f"\nPosición calculada del efector:")
print(f"X = {pos_efector[0]:.3f}, Y = {pos_efector[1]:.3f}")

# =============================================
# 6. Visualización del robot
# =============================================
def plot_robot(theta1, theta2, theta3):
    L1, L2, L3 = dh_params[0]['a'], dh_params[1]['a'], dh_params[2]['a']
    
    # Calcular posiciones de las articulaciones
    x0, y0 = 0, 0
    x1 = L1 * cos(theta1)
    y1 = L1 * sin(theta1)
    x2 = x1 + L2 * cos(theta1 + theta2)
    y2 = y1 + L2 * sin(theta1 + theta2)
    x3 = x2 + L3 * cos(theta1 + theta2 + theta3)
    y3 = y2 + L3 * sin(theta1 + theta2 + theta3)
    
    # Graficar
    plt.figure(figsize=(8, 6))
    plt.plot([x0, x1], [y0, y1], 'b-', linewidth=3, label='Eslabón 1')
    plt.plot([x1, x2], [y1, y2], 'r-', linewidth=3, label='Eslabón 2')
    plt.plot([x2, x3], [y2, y3], 'g-', linewidth=3, label='Eslabón 3')
    plt.plot(x3, y3, 'ko', markersize=8, label='Efector final')
    plt.plot(px_deseado, py_deseado, 'mx', markersize=10, label='Objetivo')
    plt.title(f'Robot RRR Planar (θ1={np.degrees(theta1):.1f}°, θ2={np.degrees(theta2):.1f}°)')
    plt.xlabel('X (m)')
    plt.ylabel('Y (m)')
    plt.axis('equal')
    plt.grid(True)
    plt.legend()
    plt.show()

plot_robot(theta1, theta2, theta3)

# Explicación del código:
# Parámetros D-H: Se definen las longitudes de los eslabones (a) y ángulos (alpha). Los theta son variables.

# Matriz D-H: La función dh_matrix() genera la matriz de transformación para cada eslabón.

# Cinemática directa: forward_kinematics() calcula la posición del efector final dados los ángulos.

# Cinemática inversa:

# Usa trigonometría para resolver theta1, theta2 y theta3.

# Considera configuraciones de "codo arriba" y "codo abajo" (descomenta la línea 45 para alternar).

# Visualización: Muestra el robot y compara la posición objetivo (✗) con la alcanzada 