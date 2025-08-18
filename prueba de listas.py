import time

# Variable para almacenar el valor anterior
valor_anterior = None

def generate_pulse_with_ramps():
    # Aquí iría tu lógica para generar pulsos con rampas
    print(f"Generando pulso con {TOTAL_PULSES} pulsos")

# Tu lista de pulsos (ejemplo)
lista_pulsos = [100, 150, 120, 200, 180]

for elemento in lista_pulsos:
    print(f"\nEjecutando {elemento}")
    TOTAL_PULSES = elemento
    
    # Comparación con el valor anterior
    if valor_anterior is not None:  # Solo compara si no es el primer elemento
        if TOTAL_PULSES > valor_anterior:
            print(f"ADVERTENCIA: El valor actual ({TOTAL_PULSES}) es MAYOR que el anterior ({valor_anterior})")
        elif TOTAL_PULSES < valor_anterior:
            print(f"INFO: El valor actual ({TOTAL_PULSES}) es MENOR que el anterior ({valor_anterior})")
        else:
            print(f"El valor actual ({TOTAL_PULSES}) es IGUAL al anterior")
    
    generate_pulse_with_ramps()
    time.sleep(1)
    
    # Actualizar el valor anterior para la próxima iteración
    valor_anterior = TOTAL_PULSES

print("\nProceso completado")