from machine import Pin
import time


PULSOS_ABSOLUTOS=0

# Configuración para la generacion de una rampa de aceleracion
GPIO_PIN_PULSOS = 21                                 # Pin GPIO a usar
GPIO_PIN_DIRECCION=22                                # Pin GPIO de direccion
GPIO_PIN_ENABLE= 18                                  # Pin GPIO de Habilitacion
pin_Pulsos = Pin(GPIO_PIN_PULSOS, Pin.OUT)           # Pin asignado para generar el tren de pulsos
pin_Direccion = Pin(GPIO_PIN_DIRECCION, Pin.OUT)     # Pin asignado para direccion
pin_habilita = Pin(GPIO_PIN_ENABLE, Pin.OUT)         # Pin asignado para habilitar
pin_Direccion.value(1)                               # Coloca el pin de direccion en HIGH
pin_habilita.value(1)                                # Coloca el pin de habilitado en HIGH
MIN_FREQ = 40                                        # Frecuencia mínima (inicio de rampa)
MAX_FREQ = 400                                       # Frecuencia máxima (frecuencia objetivo)
RAMP_RATIO = 0.05                                    # Proporción de pulsos para aceleración/frenado (30%)

lista=[200,0,200,0,200,400,0]                        # Pulsos para obtener la Posicion absoluta 

def generate_pulse_with_ramps():
    try:
        ramp_pulses = int(PULSOS_ABSOLUTOS * RAMP_RATIO)                      # Total de pulsos de la rampa
        constant_pulses = PULSOS_ABSOLUTOS - 2 * ramp_pulses                  # Total de pulsos de la velocidad constante
        
        print(f"Iniciando generación de {PULSOS_ABSOLUTOS} pulsos con rampas ...")
        print(f"Distribución: {ramp_pulses} pulsos aceleración, {constant_pulses} constantes, {ramp_pulses} frenado")

        # 1. Fase de Aceleración
        print("\n>>> Fase de Aceleración <<<")
        for i in range(ramp_pulses):
            progress = i / ramp_pulses                                    # Calcula progreso (0.0 a 1.0)
            current_freq = MIN_FREQ + (MAX_FREQ - MIN_FREQ) * progress    # Frecuencia creciente
            half_period = 0.5 / current_freq                              # Calcula semiperiodo
            # Genera el pulso
            pin_Pulsos.value(1)
            time.sleep(half_period)
            pin_Pulsos.value(0)
            time.sleep(half_period)
            
            if (i + 1) % max(1, ramp_pulses//10) == 0:                    # 10 divisiones durante la rampa
                print(f"Pulso {i+1}/{PULSOS_ABSOLUTOS} | Frec: {current_freq:.1f}Hz")

        # 2. Fase a Frecuencia Constante
        print("\n>>> Fase Constante <<<")
        half_period = 0.5 / MAX_FREQ                                      # Calcula semiperiodo
        for i in range(constant_pulses):                                  # Periodo fijo para la velocidad constante
            # Genera el pulso
            pin_Pulsos.value(1)
            time.sleep(half_period)
            pin_Pulsos.value(0)
            time.sleep(half_period)
            
            if (i + 1) % max(1, constant_pulses//10) == 0:                # 10 updates durante fase constante
                print(f"Pulso {ramp_pulses+i+1}/{PULSOS_ABSOLUTOS} | Frec: {MAX_FREQ}Hz")

        # 3. Fase de Frenado
        print("\n>>> Fase de Frenado <<<")
        for i in range(ramp_pulses):
            progress = i / ramp_pulses
            current_freq = MAX_FREQ - (MAX_FREQ - MIN_FREQ) * progress    # Frecuencia decreciente
            half_period = 0.5 / current_freq                              # Calcula semiperiodo
            # Genera el pulso
            pin_Pulsos.value(1)
            time.sleep(half_period)
            pin_Pulsos.value(0)
            time.sleep(half_period)
            
            if (i + 1) % max(1, ramp_pulses//10) == 0:                    # 10 divisiones durante frenado
                pulse_count = ramp_pulses + constant_pulses + i + 1
                print(f"Pulso {pulse_count}/{PULSOS_ABSOLUTOS} | Frec: {current_freq:.1f}Hz")

        print("\nTren de pulsos completado con rampas de aceleración y frenado")

    except KeyboardInterrupt:
        print("\nGeneración interrumpida por el usuario")
    finally:
        print("Pin limpiado y sistema detenido")       


valor_anterior = 0                           # Variable para almacenar el valor anterior

for elemento in lista:                          # evalua cada item de la lista
    print(f"Ejecutando {elemento}")
    TOTAL_PULSES = elemento                     # asigna a la variable de TOTAL_PULSE en valor de cada item de la lista
                                               
    if TOTAL_PULSES > valor_anterior:
        print(f"ADVERTENCIA: El valor actual ({TOTAL_PULSES}) es MAYOR que el anterior ({valor_anterior})")
        PULSOS_ABSOLUTOS= abs(TOTAL_PULSES - valor_anterior)
        print(f"ADVERTENCIA: El valor de PULSOS_ABSOLUTOS es: ({PULSOS_ABSOLUTOS})")
        pin_Direccion.value(1)                  # Coloca el pin de Direccion en HIGH
        print("Gira a la DERECHA")
        
    elif TOTAL_PULSES < valor_anterior:
        print(f"INFO: El valor actual ({TOTAL_PULSES}) es MENOR que el anterior ({valor_anterior})")
        PULSOS_ABSOLUTOS= abs(- TOTAL_PULSES + valor_anterior)
        print(f"ADVERTENCIA: El valor de PULSOS_ABSOLUTOS es: ({PULSOS_ABSOLUTOS})")
        pin_Direccion.value(0)                  # Coloca el pin de Direccion en LOW
        print("Gira a la IZQUIERDA")
    else:
        print(f"El valor actual ({TOTAL_PULSES}) es IGUAL al anterior")
            
    generate_pulse_with_ramps()                 # Ejecuta la funcion de rampa
    time.sleep(0.05)

    valor_anterior = TOTAL_PULSES               # Actualizar el valor anterior para la próxima iteración
    
