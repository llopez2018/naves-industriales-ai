import sys
import os
import subprocess
import json

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CORE_DIR = os.path.join(PROJECT_ROOT, "core")
AUTOCAD_DIR = os.path.join(PROJECT_ROOT, "autocad")

PYTHON_EXECUTABLE = r"C:\Users\llopez\Documents\autocad-ai-automation\venv\Scripts\python.exe"

def run_workflow(m2_area):
    print(f"--- Iniciando Orquestación Industrial FASE 2: {m2_area} m2 ---")
    
    width = int((m2_area / 1.25)**0.5)
    length = int(m2_area / width)
    num_columnas = (length // 25) * (width // 25)

    # 1. IA de Segmentación (RandLA-Net Simulator)
    print("\n[Fase 2: IA RandLA-Net] Clasificando nube de puntos del Dron...")
    subprocess.run([PYTHON_EXECUTABLE, os.path.join(CORE_DIR, "terrain_classifier.py")], check=True)
    
    with open(os.path.join(CORE_DIR, "segmentation_summary.json"), "r") as f:
        seg_data = json.load(f)
    print(f"Resultado RandLA-Net: Suelo={seg_data['ground']} pts, Veg={seg_data['vegetation']} pts")

    # 2. IA Terreno (Solo sobre puntos clasificados como 'Suelo')
    print("\n[Ingeniería] Calculando Cota Óptima sobre Suelo Limpio...")
    subprocess.run([PYTHON_EXECUTABLE, os.path.join(CORE_DIR, "calculate_optimal_grade.py")], check=True)
    
    with open(os.path.join(CORE_DIR, "terrain_results.json"), "r") as f:
        terrain_data = json.load(f)

    # 3. Agente Normativo
    print("[IA Normativa] Validando seguridad...")
    subprocess.run([PYTHON_EXECUTABLE, os.path.join(CORE_DIR, "regulatory_agent.py")], check=True)
    
    with open(os.path.join(CORE_DIR, "regulatory_report.json"), "r") as f:
        reg_data = json.load(f)

    # 4. Financiero
    print("\n[Fase 2: Financiero] Generando Presupuesto...")
    subprocess.run([PYTHON_EXECUTABLE, os.path.join(CORE_DIR, "budget_generator.py"), 
                    str(m2_area), str(terrain_data["volumen_corte_m3"]), str(num_columnas)], check=True)
    
    with open("last_budget.json", "r", encoding="utf-8") as f:
        budget_data = json.load(f)

    # 5. BIM (AutoCAD)
    print("\n[Fase 2: BIM] Generando Nave 3D...")
    subprocess.run([PYTHON_EXECUTABLE, os.path.join(AUTOCAD_DIR, "test_directo_autocad_3d.py"), 
                    str(width), str(length), str(terrain_data["cota_optima"])], check=True)

    print("\n--- Workflow Fase 2 Completado ---")
    
    final_output = {
        "budget": budget_data,
        "safety": reg_data,
        "segmentation": seg_data
    }
    
    print("FINAL_RESULT_JSON_START")
    print(json.dumps(final_output))
    print("FINAL_RESULT_JSON_END")

if __name__ == "__main__":
    area = int(sys.argv[1]) if len(sys.argv) > 1 else 50000
    run_workflow(area)
