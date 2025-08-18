import pysoem

def discover_ethercat_devices(ifname):
    """Descubre y muestra dispositivos EtherCAT en la red"""
    
    try:
        # Crear maestro EtherCAT
        master = pysoem.Master()
        
        # Configurar interfaz de red
        master.open(ifname)
        
        # Configurar tiempo de espera para operaciones
        master.config_init()
        
        # Configurar mapa de E/S
        master.config_map()
        
        # Verificar estado de los esclavos
        master.check_state()
        
        # Mostrar información de los esclavos encontrados
        print(f"\nDispositivos EtherCAT encontrados en {ifname}:")
        print(f"Número de esclavos: {master.slave_count}")
        
        for i, slave in enumerate(master.slaves):
            print(f"\nEsclavo {i}:")
            print(f"  Nombre: {slave.name.decode('utf-8')}")
            print(f"  Dirección: {slave.man}")
            print(f"  ID: {slave.id}")
            print(f"  Estado: 0x{slave.state:04X}")
            print(f"  Entradas: {slave.input_size} bytes")
            print(f"  Salidas: {slave.output_size} bytes")
            
            # Mostrar información de los registros SII (opcional)
            try:
                vendor_id = slave.sii.vendor_id
                product_code = slave.sii.product_code
                print(f"  Vendor ID: 0x{vendor_id:08X}")
                print(f"  Product Code: 0x{product_code:08X}")
            except Exception as e:
                print(f"  No se pudo leer SII: {str(e)}")
    
    except pysoem.PySoEMError as e:
        print(f"Error en EtherCAT: {str(e)}")
    
    finally:
        # Cerrar conexión
        if master.operational:
            master.state_check(pysoem.SAFEOP_STATE, 50000)
            master.write_state()
            master.state_check(pysoem.INIT_STATE, 50000)
        master.close()

if __name__ == "__main__":
    # Cambiar 'eth0' por tu interfaz de red EtherCAT
    network_interface = 'eth0'
    discover_ethercat_devices(network_interface)