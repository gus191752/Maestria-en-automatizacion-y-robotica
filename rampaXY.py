from machine import Pin
import time

# Configuración de pines para el eje X
GPIO_PIN_PULSOS_X = 21
GPIO_PIN_DIRECCION_X = 22
GPIO_PIN_ENABLE_X = 18

# Configuración de pines para el eje Y
GPIO_PIN_PULSOS_Y = 19
GPIO_PIN_DIRECCION_Y = 23
GPIO_PIN_ENABLE_Y = 5

# Configuración de parámetros de movimiento
MIN_FREQ = 40
MAX_FREQ = 400
RAMP_RATIO = 0.3  # Proporción de pulsos para aceleración/frenado

# Inicialización de pines para ambos ejes
# Eje X
pin_Pulsos_X = Pin(GPIO_PIN_PULSOS_X, Pin.OUT)
pin_Direccion_X = Pin(GPIO_PIN_DIRECCION_X, Pin.OUT)
pin_Habilita_X = Pin(GPIO_PIN_ENABLE_X, Pin.OUT)

# Eje Y
pin_Pulsos_Y = Pin(GPIO_PIN_PULSOS_Y, Pin.OUT)
pin_Direccion_Y = Pin(GPIO_PIN_DIRECCION_Y, Pin.OUT)
pin_Habilita_Y = Pin(GPIO_PIN_ENABLE_Y, Pin.OUT)

# Habilitar ambos motores
pin_Habilita_X.value(1)
pin_Habilita_Y.value(1)

# Lista de coordenadas [X, Y] a alcanzar
coordenadas = [
    [200, 100],  # Primera posición
    [200, 0],    # Segunda posición
    [200, 400],  # Tercera posición
    [50, 200]    # Cuarta posición
]

# Posición actual de los ejes
posicion_actual_X = 0
posicion_actual_Y = 0

def generar_pulsos_con_rampas(eje, pulsos_objetivo, direccion):
    """
    Genera pulsos con rampas de aceleración y desaceleración para un eje específico
    
    Args:
        eje: 'X' o 'Y' para seleccionar el eje a mover
        pulsos_objetivo: número total de pulsos a generar
        direccion: 1 para derecha/positivo, 0 para izquierda/negativo
    """
    # Seleccionar pines según el eje
    if eje == 'X':
        pin_Pulsos = pin_Pulsos_X
        pin_Direccion = pin_Direccion_X
    else:
        pin_Pulsos = pin_Pulsos_Y
        pin_Direccion = pin_Direccion_Y
    
    # Establecer dirección
    pin_Direccion.value(direccion)
    
    # Calcular distribución de pulsos
    pulsos_rampa = int(pulsos_objetivo * RAMP_RATIO)
    pulsos_constantes = pulsos_objetivo - 2 * pulsos_rampa
    
    # Ajustar si no hay suficientes pulsos para ambas rampas
    if pulsos_constantes < 0:
        pulsos_rampa = pulsos_objetivo // 2
        pulsos_constantes = 0
    
    print(f"\nEje {eje}: Generando {pulsos_objetivo} pulsos "
          f"({pulsos_rampa} aceleración, {pulsos_constantes} constantes, {pulsos_rampa} frenado)")
    
    try:
        # 1. Fase de Aceleración
        if pulsos_rampa > 0:
            for i in range(pulsos_rampa):
                progreso = i / pulsos_rampa
                frecuencia_actual = MIN_FREQ + (MAX_FREQ - MIN_FREQ) * progreso
                semiperiodo = 0.5 / frecuencia_actual
                
                pin_Pulsos.value(1)
                time.sleep(semiperiodo)
                pin_Pulsos.value(0)
                time.sleep(semiperiodo)
        
        # 2. Fase a Frecuencia Constante
        if pulsos_constantes > 0:
            semiperiodo = 0.5 / MAX_FREQ
            for i in range(pulsos_constantes):
                pin_Pulsos.value(1)
                time.sleep(semiperiodo)
                pin_Pulsos.value(0)
                time.sleep(semiperiodo)
        
        # 3. Fase de Frenado
        if pulsos_rampa > 0:
            for i in range(pulsos_rampa):
                progreso = i / pulsos_rampa
                frecuencia_actual = MAX_FREQ - (MAX_FREQ - MIN_FREQ) * progreso
                semiperiodo = 0.5 / frecuencia_actual
                
                pin_Pulsos.value(1)
                time.sleep(semiperiodo)
                pin_Pulsos.value(0)
                time.sleep(semiperiodo)
                
    except KeyboardInterrupt:
        print(f"\nMovimiento del eje {eje} interrumpido")
    finally:
        print(f"Movimiento del eje {eje} completado")

def mover_eje_sincronizado(objetivo_X, objetivo_Y):
    """
    Mueve ambos ejes de forma sincronizada a sus posiciones objetivo
    
    Args:
        objetivo_X: posición objetivo para el eje X
        objetivo_Y: posición objetivo para el eje Y
    """
    global posicion_actual_X, posicion_actual_Y
    
    # Calcular pulsos necesarios para cada eje
    pulsos_X = abs(objetivo_X - posicion_actual_X)
    pulsos_Y = abs(objetivo_Y - posicion_actual_Y)
    
    # Determinar direcciones
    dir_X = 1 if objetivo_X > posicion_actual_X else 0
    dir_Y = 1 if objetivo_Y > posicion_actual_Y else 0
    
    print(f"\nMovimiento: X({posicion_actual_X}→{objetivo_X}), "
          f"Y({posicion_actual_Y}→{objetivo_Y})")
    
    # Si ambos ejes necesitan moverse
    if pulsos_X > 0 and pulsos_Y > 0:
        # Calcular la relación de velocidades
        if pulsos_X >= pulsos_Y:
            pulsos_principales = pulsos_X
            pulsos_secundarios = pulsos_Y
            eje_principal = 'X'
            eje_secundario = 'Y'
            dir_principal = dir_X
            dir_secundario = dir_Y
        else:
            pulsos_principales = pulsos_Y
            pulsos_secundarios = pulsos_X
            eje_principal = 'Y'
            eje_secundario = 'X'
            dir_principal = dir_Y
            dir_secundario = dir_X
        
        # Configurar direcciones
        pin_Direccion_X.value(dir_X)
        pin_Direccion_Y.value(dir_Y)
        
        # Calcular relación de pasos
        relacion_pasos = pulsos_principales / pulsos_secundarios if pulsos_secundarios > 0 else 1
        
        # Generar pulsos de forma sincronizada
        for paso in range(pulsos_principales):
            # Generar pulso para el eje principal
            pin_Pulsos_X.value(1) if eje_principal == 'X' else pin_Pulsos_Y.value(1)
            
            # Generar pulso para el eje secundario cuando corresponda
            if paso % relacion_pasos < 1 and paso * relacion_pasos <= pulsos_secundarios:
                pin_Pulsos_X.value(1) if eje_secundario == 'X' else pin_Pulsos_Y.value(1)
            
            # Semiperiodo de espera
            time.sleep(0.5 / MAX_FREQ)
            
            # Apagar todos los pulsos
            pin_Pulsos_X.value(0)
            pin_Pulsos_Y.value(0)
            
            # Segundo semiperiodo de espera
            time.sleep(0.5 / MAX_FREQ)
    
    # Si solo un eje necesita moverse
    elif pulsos_X > 0:
        generar_pulsos_con_rampas('X', pulsos_X, dir_X)
    elif pulsos_Y > 0:
        generar_pulsos_con_rampas('Y', pulsos_Y, dir_Y)
    
    # Actualizar posiciones actuales
    posicion_actual_X = objetivo_X
    posicion_actual_Y = objetivo_Y

# Programa principal
try:
    print("Iniciando sistema de control de dos ejes")
    
    for coord in coordenadas:
        objetivo_X, objetivo_Y = coord
        print(f"\n--- Moviendo a posición X={objetivo_X}, Y={objetivo_Y} ---")
        
        mover_eje_sincronizado(objetivo_X, objetivo_Y)
        time.sleep(1)  # Pausa entre movimientos
    
    print("\nSecuencia de movimientos completada")

except KeyboardInterrupt:
    print("\nPrograma interrumpido por el usuario")

finally:
    # Deshabilitar motores y limpiar
    pin_Habilita_X.value(0)
    pin_Habilita_Y.value(0)
    pin_Pulsos_X.value(0)
    pin_Pulsos_Y.value(0)
    print("Motores deshabilitados y pines limpiados")