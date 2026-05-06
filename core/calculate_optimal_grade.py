import numpy as np
from scipy.optimize import minimize_scalar
import os
import json

def load_drone_data(filename):
    x_coords, y_coords, z_coords = [], [], []
    if not os.path.exists(filename):
        raise FileNotFoundError(f"El archivo {filename} no fue encontrado.")
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith("#") or line.strip() == "": continue
            parts = line.strip().split()
            if len(parts) >= 3:
                x_coords.append(float(parts[0]))
                y_coords.append(float(parts[1]))
                z_coords.append(float(parts[2]))
    return np.array(x_coords), np.array(y_coords), np.array(z_coords)

def calculate_volumes(target_z, terrain_z, grid_area):
    diff = terrain_z - target_z
    corte_mask = diff > 0
    relleno_mask = diff < 0
    vol_corte = np.sum(diff[corte_mask]) * grid_area
    vol_relleno = np.abs(np.sum(diff[relleno_mask]) * grid_area)
    return vol_corte, vol_relleno

def cost_function(target_z, terrain_z, grid_area, unit_cost_corte=135, unit_cost_relleno=150, cost_acarreo=90):
    vol_corte, vol_relleno = calculate_volumes(target_z, terrain_z, grid_area)
    costo_base = (vol_corte * unit_cost_corte) + (vol_relleno * unit_cost_relleno)
    desbalance = abs(vol_corte - vol_relleno)
    costo_penalizacion = desbalance * cost_acarreo
    return costo_base + costo_penalizacion

def find_optimal_grade(terrain_z, grid_area):
    z_min = np.min(terrain_z)
    z_max = np.max(terrain_z)
    result = minimize_scalar(cost_function, bounds=(z_min, z_max), args=(terrain_z, grid_area), method='bounded')
    return result.x

if __name__ == "__main__":
    xyz_file = os.path.join(os.path.dirname(__file__), "terreno_real_dron.xyz")
    try:
        X, Y, Z_terrain = load_drone_data(xyz_file)
        grid_res = 5 
        area_por_punto = grid_res * grid_res
        
        cota_optima = find_optimal_grade(Z_terrain, area_por_punto)
        corte, relleno = calculate_volumes(cota_optima, Z_terrain, area_por_punto)
        
        # Exportar a JSON para Orquestador y AutoCAD
        results = {
            "cota_optima": float(cota_optima),
            "volumen_corte_m3": float(corte),
            "volumen_relleno_m3": float(relleno)
        }
        out_path = os.path.join(os.path.dirname(__file__), "terrain_results.json")
        with open(out_path, "w") as f:
            json.dump(results, f, indent=4)
            
        print(f"Cota ideal: {cota_optima:.3f}m | Corte: {corte:,.2f}m3")
    except Exception as e:
        print(f"Error procesando topografía: {e}")
