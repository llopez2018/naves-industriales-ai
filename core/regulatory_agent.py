import json
import os

def analyze_safety_and_norms(target_z, max_terrain_z, cut_volume):
    """
    Simula el razonamiento de un Agente LLM (Director Responsable de Obra).
    Valida los taludes resultantes contra el Reglamento de Construcciones (RCDF)
    y la NOM-031-STPS.
    """
    # Calculamos la altura máxima del corte (El cerro más alto vs nuestra plataforma)
    max_cut_depth = max_terrain_z - target_z
    
    report = {
        "depth_meters": round(max_cut_depth, 2),
        "status": "PASS",
        "warnings": [],
        "requirements": [],
        "norm_references": ["NOM-031-STPS (Construcción)", "RCDF Art. 180 (Excavaciones)"]
    }

    # Lógica de Validación Normativa
    if max_cut_depth > 1.5:
        report["status"] = "WARNING"
        report["warnings"].append(f"Corte profundo detectado ({report['depth_meters']}m).")
        report["requirements"].append("Obligatorio: Ademe o apuntalamiento preventivo según NOM-031.")
        
    if max_cut_depth > 5.0:
        report["status"] = "CRITICAL"
        report["warnings"].append("Talud inestable. Riesgo de deslizamiento detectado.")
        report["requirements"].append("Obligatorio: Construcción de Muro de Contención Estructural.")
        report["requirements"].append("Requerido: Estudio de mecánica de suelos específico para estabilidad de taludes.")
    
    if cut_volume > 100000:
        report["warnings"].append("Volumen masivo de excavación. Se requiere plan de manejo de residuos (RME).")

    return report

if __name__ == "__main__":
    # 1. Leer resultados de la IA de Terreno
    results_path = os.path.join(os.path.dirname(__file__), "terrain_results.json")
    xyz_path = os.path.join(os.path.dirname(__file__), "terreno_real_dron.xyz")
    
    try:
        with open(results_path, "r") as f:
            t_data = json.load(f)
        
        # Obtener el punto más alto del terreno real del dron
        max_z = 73.0 # Fallback basado en nuestro .xyz
        if os.path.exists(xyz_path):
            with open(xyz_path, "r") as f:
                z_vals = [float(l.split()[2]) for l in f if not l.startswith("#") and l.strip()]
                max_z = max(z_vals)

        # 2. Ejecutar análisis del Agente Normativo
        analysis = analyze_safety_and_norms(t_data["cota_optima"], max_z, t_data["volumen_corte_m3"])
        
        # 3. Guardar el reporte para el Frontend
        with open(os.path.join(os.path.dirname(__file__), "regulatory_report.json"), "w") as f:
            json.dump(analysis, f, indent=4)
            
        print(f"Análisis Normativo Completado. Estatus: {analysis['status']}")
        
    except Exception as e:
        print(f"Error en Agente Normativo: {e}")
