import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from math import cos, sin, atan2, sqrt, pi

# =============================================
# 1. Parámetros D-H modificados para robot tipo Cobot UR5e (en mm)
# =============================================
# Eslabón | theta (θ) | d | a | alpha (α)

dh_params = [
    {'theta': 0, 'd': 89.2,   'a': 0,        'alpha':  pi/2  },   # Eslabón 1 (Base)
    {'theta': 0, 'd': 0,      'a': 425.0,    'alpha':   0    },   # Eslabón 2 (Hombro)
    {'theta': 0, 'd': 0,      'a': 392.0,    'alpha':   0    },   # Eslabón 3 (Codo)
    {'theta': 0, 'd': 109.3,  'a': 0,        'alpha':  pi/2  },   # Eslabón 4 (Muñeca 1)
    {'theta': 0, 'd': 94.75,  'a': 0,        'alpha': -pi/2  },   # Eslabón 5 (Muñeca 2)
    {'theta': 0, 'd': 82.5,   'a': 0,        'alpha':   0    }    # Eslabón 6 (Efector final)
]

# =============================================
# 2. Función para matriz de transformación D-H
# =============================================
def dh_matrix(theta, d, a, alpha):
    A = np.array([
        [cos(theta),   -sin(theta)*cos(alpha),   sin(theta)*sin(alpha),   a*cos(theta)],
        [sin(theta),    cos(theta)*cos(alpha),  -cos(theta)*sin(alpha),   a*sin(theta)],
        [    0,              sin(alpha),              cos(alpha),              d      ],
        [    0,                  0,                       0,                   1      ]
    ])
    return A

# =============================================
# 3. Función para matriz de rotación RPY (Roll, Pitch, Yaw)
# =============================================
def rpy_matrix(roll, pitch, yaw):
    # Rotación en Z (yaw)
    Rz = np.array([
        [cos(yaw), -sin(yaw), 0],
        [sin(yaw),  cos(yaw), 0],
        [0,         0,       1]
    ])
    
    # Rotación en Y (pitch)
    Ry = np.array([
        [cos(pitch),  0,  sin(pitch)],
        [0,           1,          0],
        [-sin(pitch), 0,  cos(pitch)]
    ])
    
    # Rotación en X (roll)
    Rx = np.array([
        [1,        0,         0],
        [0, cos(roll), -sin(roll)],
        [0, sin(roll),  cos(roll)]
    ])
    
    # Rotación compuesta
    R = Rz @ Ry @ Rx
    return R

# =============================================
# 4. Función para crear matriz de transformación homogénea desde RPY y posición
# =============================================
def create_target_matrix(x, y, z, roll, pitch, yaw):
    R = rpy_matrix(roll, pitch, yaw)
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = [x, y, z]
    return T

# =============================================
# 5. Cinemática directa
# =============================================
def forward_kinematics(thetas):
    T = np.eye(4)
    for i in range(6):
        T = T @ dh_matrix(thetas[i], dh_params[i]['d'], dh_params[i]['a'], dh_params[i]['alpha'])
    return T

# =============================================
# 6. Cinemática inversa mejorada
# =============================================
def inverse_kinematics(T_deseada):
    # Posición y orientación deseada
    px, py, pz = T_deseada[0, 3], T_deseada[1, 3], T_deseada[2, 3]
    n, s, a = T_deseada[:3, :3].T  # Vectores de orientación
    
    # Posición del centro de muñeca (considerando el offset del efector final)
    d6 = dh_params[5]['d']
    pw = np.array([px - d6*a[0], py - d6*a[1], pz - d6*a[2]])

    print("Centro de muñeca (pw):", pw)
    
    # Solución para theta1
    theta1 = atan2(pw[1], pw[0])
    
    # Solución para theta2 y theta3
    # Ajuste importante: usar a2 y a3 en lugar de L2 y L3
    a2 = dh_params[1]['a']
    a3 = dh_params[2]['a']
    d1 = dh_params[0]['d']
    d2 = dh_params[1]['d']
    d3 = dh_params[2]['d']
    
    # Proyección en el plano XY
    r = sqrt(pw[0]**2 + pw[1]**2) - a2
    # Altura relativa
    h = pw[2] - d1 - d2 - d3
    
    # Ley de cosenos para theta3
    D = (r**2 + h**2 - a2**2 - a3**2) / (2 * a2 * a3)
    
    if abs(D) > 1:
        print("Advertencia: La posición deseada puede ser inalcanzable")
        D = np.clip(D, -1, 1)
    
    theta3 = atan2(-sqrt(1 - D**2), D)  # Solución con codo abajo
    
    # Cálculo de theta2
    k1 = a2 + a3 * cos(theta3)
    k2 = a3 * sin(theta3)
    theta2 = atan2(h, r) - atan2(k2, k1)
    
    # Solución para theta4, theta5, theta6
    A1 = dh_matrix(theta1, dh_params[0]['d'], dh_params[0]['a'], dh_params[0]['alpha'])
    A2 = dh_matrix(theta2, dh_params[1]['d'], dh_params[1]['a'], dh_params[1]['alpha'])
    A3 = dh_matrix(theta3, dh_params[2]['d'], dh_params[2]['a'], dh_params[2]['alpha'])
    T03 = A1 @ A2 @ A3
    R03 = T03[:3, :3]
    R06 = T_deseada[:3, :3]
    R36 = np.linalg.inv(R03) @ R06
    
    # Ángulos Euler ZYZ
    theta5 = atan2(sqrt(R36[0,2]**2 + R36[1,2]**2), R36[2,2])
    if abs(theta5) > 1e-6:
        theta4 = atan2(R36[1,2], R36[0,2])
        theta6 = atan2(R36[2,1], -R36[2,0])
    else:
        theta4 = 0
        theta6 = atan2(-R36[0,1], R36[0,0])
    
    return [theta1, theta2, theta3, theta4, theta5, theta6]

# =============================================
# 7. Ejemplo de uso con posición y orientación en RPY
# =============================================
# Definir posición deseada (x, y, z) en mm
posicion_deseada = [450, 430, 460]  # x, y, z

# Definir orientación deseada en ángulos RPY (radianes)
roll_deseado =   pi/2    # Rotación alrededor del eje X
pitch_deseado =  pi/8    # Rotación alrededor del eje Y (90° hacia abajo)
yaw_deseado =   -pi/2    # Rotación alrededor del eje Z

# Crear matriz de transformación deseada
T_deseada = create_target_matrix(
    posicion_deseada[0], posicion_deseada[1], posicion_deseada[2],
    roll_deseado, pitch_deseado, yaw_deseado
)

print("Posición deseada del efector final:", posicion_deseada)
print("Orientación deseada (RPY) [rad]:", [roll_deseado, pitch_deseado, yaw_deseado])

# Resolver cinemática inversa
thetas = inverse_kinematics(T_deseada)
print("\nÁngulos articulares calculados (radianes):", np.round(thetas, 3))
print("Ángulos articulares calculados (grados):", np.round(np.degrees(thetas), 3))

# Verificar con cinemática directa
T_calculada = forward_kinematics(thetas)
print("\nPosición calculada del efector final:", np.round(T_calculada[:3, 3], 4))
print("Orientación calculada (matriz):\n", np.round(T_calculada[:3, :3], 4))

# =============================================
# 8. Visualización 3D
# =============================================
def plot_robot_3d(thetas):
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Calcular todas las transformaciones
    T = np.eye(4)
    points = [T[:3, 3]]
    transforms = []
    
    for i in range(6):
        T = T @ dh_matrix(thetas[i], dh_params[i]['d'], dh_params[i]['a'], dh_params[i]['alpha'])
        transforms.append(T)
        points.append(T[:3, 3])
    
    points = np.array(points)
    
    # Calcular el centro de muñeca
    d6 = dh_params[5]['d']
    a = T_deseada[:3, 2]  # Vector de aproximación
    pw_calculado = np.array([
        T_deseada[0,3] - d6*a[0],
        T_deseada[1,3] - d6*a[1],
        T_deseada[2,3] - d6*a[2]
    ])
    
    def draw_frame(T, length=50):  # Longitud aumentada para mejor visualización
        ax.quiver(T[0,3], T[1,3], T[2,3], T[0,0], T[1,0], T[2,0], color='r', length=length)
        ax.quiver(T[0,3], T[1,3], T[2,3], T[0,1], T[1,1], T[2,1], color='g', length=length)
        ax.quiver(T[0,3], T[1,3], T[2,3], T[0,2], T[1,2], T[2,2], color='b', length=length)
    
    draw_frame(T_deseada, length=75)
    draw_frame(T_calculada, length=50)

    # Graficar
    ax.plot(points[:,0], points[:,1], points[:,2], 'o-', linewidth=2, markersize=8, label='Robot')
    
    # Puntos clave
    ax.scatter(points[-1,0], points[-1,1], points[-1,2], color='red', s=150, label='Efector Final')
    ax.scatter(pw_calculado[0], pw_calculado[1], pw_calculado[2], 
               color='blue', s=200, marker='x', label='Centro Muñeca (pw)')
    ax.scatter(T_deseada[0,3], T_deseada[1,3], T_deseada[2,3], 
               color='green', s=200, marker='*', label='Posición Deseada')
    
    ax.set_xlabel('X (mm)', fontsize=12)
    ax.set_ylabel('Y (mm)', fontsize=12)
    ax.set_zlabel('Z (mm)', fontsize=12)
    ax.set_title(f'UR5e - Posición: {posicion_deseada} mm, Orientación: RPY(roll={np.round(np.degrees(roll_deseado))}°, pitch={np.round(np.degrees(pitch_deseado))}°, yaw={np.round(np.degrees(yaw_deseado))}°)', fontsize=12)
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(True)
    
    # Ajustar límites para mejor visualización
    max_range = max(posicion_deseada) * 1.5
    ax.set_xlim([0, max_range])
    ax.set_ylim([0, max_range])
    ax.set_zlim([0, max_range])
    
    plt.tight_layout()
    plt.show()

    

    

plot_robot_3d(thetas)