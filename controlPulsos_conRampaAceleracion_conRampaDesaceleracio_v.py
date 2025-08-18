from machine import Pin
import time

# Configuración para la generacion de una rampa de aceleracion
GPIO_PIN_PULSOS = 21                                 # Pin GPIO a usar
GPIO_PIN_DIRECCION=22                                # Pin GPIO de direccion
GPIO_PIN_ENABLE= 18                                  # Pin GPIO de Habilitacion
pin_Pulsos = Pin(GPIO_PIN_PULSOS, Pin.OUT)           # Pin asignado para generar el tren de pulsos
pin_Direccion = Pin(GPIO_PIN_DIRECCION, Pin.OUT)     # Pin asignado para direccion
pin_habilita = Pin(GPIO_PIN_ENABLE, Pin.OUT)         # Pin asignado para habilitar
pin_Direccion.value(1)                               # Coloca el pin de direccion en HIGH
pin_habilita.value(1)                                # Coloca el pin de habilitado en HIGH
MIN_FREQ = 20                                        # Frecuencia mínima (inicio de rampa)
MAX_FREQ = 500                                       # Frecuencia máxima (frecuencia objetivo)
TOTAL_PULSES = 400                                   # Número total de pulsos a generar
RAMP_RATIO = 0.05                                    # Proporción de pulsos para aceleración/frenado (30%)

def generate_pulse_with_ramps():
    try:
        ramp_pulses = int(TOTAL_PULSES * RAMP_RATIO)                      # Total de pulsos de la rampa
        constant_pulses = TOTAL_PULSES - 2 * ramp_pulses                  # Total de pulsos de la velocidad constante
        
        print(f"Iniciando generación de {TOTAL_PULSES} pulsos con rampas ...")
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
                print(f"Pulso {i+1}/{ramp_pulses} | Frec: {current_freq:.1f}Hz")

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
                print(f"Pulso {ramp_pulses+i+1}/{TOTAL_PULSES} | Frec: {MAX_FREQ}Hz")

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
            
            if (i + 1) % max(1, ramp_pulses//10) == 0:  # 10 divisiones durante frenado
                pulse_count = ramp_pulses + constant_pulses + i + 1
                print(f"Pulso {pulse_count}/{TOTAL_PULSES} | Frec: {current_freq:.1f}Hz")

        print("\nTren de pulsos completado con rampas de aceleración y frenado")

    except KeyboardInterrupt:
        print("\nGeneración interrumpida por el usuario")
    finally:
        pin_Pulsos.value(0)                                  # Coloca el pin de tren de pulsos en LOW
        pin_Direccion.value(0)                               # Coloca el pin de direccion en LOW
        pin_habilita.value(0)                                # Coloca el pin de enable en LOW
        print("Pin limpiado y sistema detenido")       

if __name__ == "__main__":
    generate_pulse_with_ramps()