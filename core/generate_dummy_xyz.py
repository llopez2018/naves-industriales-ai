import numpy as np
import random

def generate_drone_data(filename, width, length, resolution=5):
    """
    Genera un archivo de nube de puntos .xyz que imita los datos de un Dron RTK.
    Simula un terreno con pendientes marcadas, montículos y depresiones aleatorias.
    """
    print(f"Generando datos de vuelo de dron simulados en {filename}...")
    
    with open(filename, 'w') as f:
        # Escribir cabecera (algunos softwares piden cabecera, otros no, la dejaremos comentada)
        f.write("# Archivo de Nube de Puntos (Simulación Dron DJI M300 RTK)\n")
        f.write("# Formato: X Y Z (Metros)\n")
        
        # Simular una colina que cruza el terreno en diagonal
        for x in range(0, length, resolution):
            for y in range(0, width, resolution):
                # Ecuación compleja para generar un terreno natural y muy irregular
                # Altura base de 50 metros sobre el nivel del mar
                base_z = 50.0 
                # Pendiente natural del 5% hacia el norte
                slope = (y * 0.05) 
                # Una colina grande en el medio usando Gaussianas
                hill = 15.0 * np.exp(-(((x - length/2)**2) + ((y - width/2)**2)) / 5000.0)
                # Pequeños baches y montículos aleatorios (ruido topográfico)
                noise = random.uniform(-0.5, 0.5)
                
                z = base_z + slope + hill + noise
                
                # Escribir la línea (X, Y, Z)
                f.write(f"{float(x):.2f} {float(y):.2f} {float(z):.2f}\n")
    
    print(f"Archivo {filename} generado exitosamente.")

if __name__ == "__main__":
    # Generamos un área de 300x300m (suficiente para una nave grande)
    generate_drone_data("terreno_real_dron.xyz", 300, 300, 5)
