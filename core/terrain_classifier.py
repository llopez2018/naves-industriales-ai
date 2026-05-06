import numpy as np
import os
import json

class RandLANetSimulator:
    """
    Simulador del pipeline de RandLA-Net para segmentacion semantica de nubes de puntos.
    Objetivo: Clasificar puntos en Suelo (2), Vegetacion (3) y Estructuras (6).
    """
    def __init__(self):
        self.labels = {
            1: "Sin Clasificar",
            2: "Suelo (Ground)",
            3: "Vegetacion Alta",
            6: "Estructuras/Edificios"
        }

    def classify_points(self, points):
        """
        Emula el modulo Local Feature Aggregation de RandLA-Net.
        Analiza la rugosidad y varianza local para asignar etiquetas.
        """
        print(f"RandLA-Net: Procesando {len(points)} puntos...")
        
        # 1. Extraer coordenadas
        z_coords = points[:, 2]
        
        # 2. Heuristica de clasificacion (Simulacion de Inferencia)
        # En RandLA-Net real, esto lo haria la red neuronal analizando vecinos
        classified_data = []
        
        z_mean = np.mean(z_coords)
        z_std = np.std(z_coords)

        for p in points:
            x, y, z = p
            label = 2 # Por defecto es suelo
            
            # Simulacion: Si el punto es mucho mas alto que el promedio local, es vegetacion
            if z > (z_mean + z_std * 0.8):
                label = 3 # Vegetacion
            elif z > (z_mean + z_std * 1.5):
                label = 6 # Estructura
                
            classified_data.append([x, y, z, label])
            
        return np.array(classified_data)

def run_segmentation():
    xyz_file = os.path.join(os.path.dirname(__file__), "terreno_real_dron.xyz")
    output_file = os.path.join(os.path.dirname(__file__), "terreno_segmentado.xyz")
    
    if not os.path.exists(xyz_file):
        print("Error: No se encontro el archivo del dron.")
        return

    # Cargar puntos
    data = np.loadtxt(xyz_file, comments="#")
    
    # Ejecutar RandLA-Net Simulator
    model = RandLANetSimulator()
    classified_points = model.classify_points(data)
    
    # Guardar nube segmentada (X, Y, Z, Label)
    header = "X Y Z Label(2:Ground, 3:Veg, 6:Struct)"
    np.savetxt(output_file, classified_points, fmt="%.3f %.3f %.3f %d", header=header)
    
    # Generar resumen para el Frontend
    counts = {
        "total": len(classified_points),
        "ground": int(np.sum(classified_points[:, 3] == 2)),
        "vegetation": int(np.sum(classified_points[:, 3] == 3)),
        "structures": int(np.sum(classified_points[:, 3] == 6))
    }
    
    with open(os.path.join(os.path.dirname(__file__), "segmentation_summary.json"), "w") as f:
        json.dump(counts, f, indent=4)
        
    print(f"Segmentacion completada. Suelo detectado: {counts['ground']} puntos.")

if __name__ == "__main__":
    run_segmentation()
