import roboticstoolbox as rtb
from roboticstoolbox import DHRobot, RevoluteDH
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# ==================Definicion de Manipuladores===========================
# ==================Definicion las longitudes de los eslabones===========================

l1 = 0.0892  # Eslabón 1 (Base)
l2 = 0.425   # Eslabón 2 (Hombro
l3 = 0.392   # Eslabón 3 (Codo)
l4 = 0.1093  # Eslabón 4 (Muñeca 1)
l5 = 0.09475 # Eslabón 5 (Muñeca 2)
l6 = 0.0825  # Eslabón 6 (Efector final)    

# ==================Definir la matriz denavit hetemberg ===========================

l1 = rtb.RevoluteDH(d=l1,  a=0,   alpha=np.pi/2,    offset=0, name='Base')
l2 = rtb.RevoluteDH(d=0,   a=l2,  alpha=0,          offset=0, name='Hombro')
l1 = rtb.RevoluteDH(d=0,   a=l3,  alpha=0,          offset=0, name='Codo')
   

# ==================Crear el robot serial con serial link==========================
robot= rtb.SerialLink(l1,l2,l3, name='UR5e')
  
# ==================Graficar el robot==========================
robot.teach([0,0,0],limits=[-1,1,-1,1,0,1]) # Configuración inicial del robot

# ==================Muestra el grafico==========================
plt.show()
