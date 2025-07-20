import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from math import cos, sin, atan2, sqrt, pi

# =============================================
# 1. Parámetros D-H modificados para robot tipo Cobot UR5e
# =============================================
# Eslabón | theta (θ) | d | a | alpha (α)
dh_params = [
    {'theta': 0, 'd': 0.08916,  'a': 0,        'alpha':  pi/2  },   # Eslabón 1 (Base)
    {'theta': 0, 'd': 0,        'a': 0.425,    'alpha':   0    },   # Eslabón 2 (Hombro)
    {'theta': 0, 'd': 0,        'a': 0.39225,  'alpha':   0    },   # Eslabón 3 (Codo)
    {'theta': 0, 'd': 0.10915,  'a': 0,        'alpha':  pi/2  },   # Eslabón 4 (Muñeca 1)
    {'theta': 0, 'd': 0.09456,  'a': 0,        'alpha': -pi/2  },   # Eslabón 5 (Muñeca 2)
    {'theta': 0, 'd': 0.0823,   'a': 0,        'alpha':   0    }    # Eslabón 6 (Efector final)
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
# 3. Cinemática directa
# =============================================
def forward_kinematics(thetas):
    T = np.eye(4)
    for i in range(6):
        T = T @ dh_matrix(thetas[i], dh_params[i]['d'], dh_params[i]['a'], dh_params[i]['alpha'])
    return T

# =============================================
# 4. Cinemática inversa mejorada
# =============================================
def inverse_kinematics(T_deseada):
    # Posición y orientación deseada
    px, py, pz = T_deseada[0, 3], T_deseada[1, 3], T_deseada[2, 3]
    n, s, a = T_deseada[:3, :3].T  # Vectores de orientación
    
    # Posición del centro de muñeca
    d6 = dh_params[5]['d']
    pw = np.array([px - d6*a[0], py - d6*a[1], pz - d6*a[2]])

    print("Centro de muñeca (pw):", pw)   ###  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<  
    
    # Solución para theta1, theta2, theta3


    # Theta1 tiene dos soluciones posibles
    theta1 = atan2(pw[1], pw[0])                                 ### solucion con hombro derecho 
    #theta1 = theta1 + pi if theta1 < 0 else theta1 - pi           ### solucion con hombro izquierdo
    
    # Solución para theta2 y theta3
    r = sqrt(pw[0]**2 + pw[1]**2) - dh_params[1]['a']
    h = pw[2] - dh_params[0]['d']
    L2 = dh_params[1]['a']
    L3 = dh_params[2]['a']
    
    D = (r**2 + h**2 - L2**2 - L3**2) / (2 * L2 * L3)
    
    # Verificar si la posición es alcanzable
    if abs(D) > 1:
        print("Advertencia: La posición deseada puede ser inalcanzable")
        D = np.clip(D, -1, 1)  # Limitar al rango válido
    

    ####  Dos posibles soluciones para theta3
    ####  solucio  con codo arriba
    ####  solucion con codo abajo
    #theta3 = atan2(sqrt(1 - D**2), D)         # Solución con codo arriba
    theta3 = atan2(-sqrt(1 - D**2), D)       # Solución con codo abajo
    
    #theta2 = atan2(h, r) - atan2(L3*sin(theta3), L2 + L3*cos(theta3))        # Solución con codo arriba
    theta2 = atan2(h, r) - atan2(L3*sin(theta3), L2 + L3*cos(theta3))         # Solución con codo abajo
    
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
    if abs(theta5) > 1e-6:  # Evitar singularidad
        theta4 = atan2(R36[1,2], R36[0,2])
        theta6 = atan2(R36[2,1], -R36[2,0])
    else:
        # Caso de singularidad (theta5 = 0 o pi)
        theta4 = 0
        theta6 = atan2(-R36[0,1], R36[0,0])
    
    return [theta1, theta2, theta3, theta4, theta5, theta6]

# =============================================
# 5. Ejemplo de uso con posición alcanzable
# =============================================
# Posición objetivo dentro del espacio de trabajo

T_deseada = np.array([
    [0,    1,    0,  0.6],    # X global
    [-1,   0,    0,  0.5],      # Y invertido (para orientación hacia abajo)
    [0,    0,    1,  0.6],   # -Z  (efector hacia abajo)
    [0,    0,    0,   1 ]
])
# Imprimir posición deseada (efector final)
print("Posición deseada del efector final :", T_deseada[:3, 3])  ##  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< 

# Resolver cinemática inversa
thetas = inverse_kinematics(T_deseada)
print("Ángulos articulares calculados (radianes):",np.round(thetas, 3))  ## <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< 

# Verificar con cinemática directa
T_calculada = forward_kinematics(thetas)
print("\nPosición calculada del efector final:", np.round(T_calculada[:3, 3], 3))  ## <<<<<<<<<<<<<<<<<<<<<<<<<<<<<  


# =============================================
# 6. Visualización 3D
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
    
    # Calcular EXACTAMENTE el mismo pw que en inverse_kinematics
    d6 = dh_params[5]['d']
    a = T_deseada[:3, 2]  # Vector de aproximación (tercera columna de T_deseada)
    pw_calculado = np.array([
        T_deseada[0,3] - d6*a[0],
        T_deseada[1,3] - d6*a[1],
        T_deseada[2,3] - d6*a[2]
    ])
    
    def draw_frame(T, length=0.1):
        ax.quiver(T[0,3], T[1,3], T[2,3], T[0,0], T[1,0], T[2,0], color='r', length=length)
        ax.quiver(T[0,3], T[1,3], T[2,3], T[0,1], T[1,1], T[2,1], color='g', length=length)
        ax.quiver(T[0,3], T[1,3], T[2,3], T[0,2], T[1,2], T[2,2], color='b', length=length)
    
    draw_frame(T_deseada)
    draw_frame(T_calculada)


    # Graficar
    ax.plot(points[:,0], points[:,1], points[:,2], 'o-', linewidth=2, markersize=8, label='Robot')
    
    # Puntos clave
    ax.scatter(points[-1,0], points[-1,1], points[-1,2], color='red', s=150, label='Efector Final')
    ax.scatter(pw_calculado[0], pw_calculado[1], pw_calculado[2], 
               color='blue', s=200, marker='x', label='Centro Muñeca (pw calculado)')
    ax.scatter(T_deseada[0,3], T_deseada[1,3], T_deseada[2,3], 
               color='green', s=200, marker='*', label='Posición Deseada')
    
    ax.set_xlabel('X (m)', fontsize=12)
    ax.set_ylabel('Y (m)', fontsize=12)
    ax.set_zlabel('Z (m)', fontsize=12)
    ax.set_title('UR5e - Verificación Exacta de Posiciones', fontsize=14)
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(True)
    plt.show()
plot_robot_3d(thetas)


