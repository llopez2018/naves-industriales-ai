import sys
import json

def generate_budget(area_m2, vol_tierra_m3, num_columnas, height=10):
    """
    Genera un presupuesto paramétrico basado en estándares industriales.
    Precios unitarios (MXN) estimados:
    - Mov. Tierras (promedio): $135 / m3
    - Piso Industrial (concreto armado): $950 / m2
    - Estructura Metálica (techumbre): $2,400 / m2
    - Muros perimetrales (paneles): $1,400 / m2 vertical
    - Columnas (concreto/acero): $18,500 / pz
    """
    
    # 1. Movimiento de tierras
    costo_tierras = vol_tierra_m3 * 135
    
    # 2. Cimentación y Piso
    costo_piso = area_m2 * 950
    
    # 3. Estructura y Columnas
    costo_columnas = num_columnas * 18500
    costo_techumbre = area_m2 * 2400
    
    # 4. Envolvente (Muros)
    # Asumiendo planta rectangular para el perímetro
    width = int((area_m2 / 1.25)**0.5)
    length = int(area_m2 / width)
    perimetro = 2 * (length + width)
    area_muros = perimetro * height
    costo_muros = area_muros * 1400
    
    # 5. Totales
    subtotal = costo_tierras + costo_piso + costo_columnas + costo_techumbre + costo_muros
    indirectos = subtotal * 0.15 # 15% (Administración, utilidad, imprevistos)
    total = subtotal + indirectos
    
    budget = {
        "conceptos": [
            {"nombre": "Movimiento de Tierras", "costo": round(costo_tierras, 2), "pct": round((costo_tierras/total)*100, 1)},
            {"nombre": "Piso Industrial (concreto)", "costo": round(costo_piso, 2), "pct": round((costo_piso/total)*100, 1)},
            {"nombre": "Estructura y Techumbre", "costo": round(costo_techumbre, 2), "pct": round((costo_techumbre/total)*100, 1)},
            {"nombre": "Columnas Estructurales", "costo": round(costo_columnas, 2), "pct": round((costo_columnas/total)*100, 1)},
            {"nombre": "Envolvente (Muros)", "costo": round(costo_muros, 2), "pct": round((costo_muros/total)*100, 1)}
        ],
        "resumen": {
            "subtotal": round(subtotal, 2),
            "indirectos": round(indirectos, 2),
            "total_estimado": round(total, 2),
            "costo_por_m2": round(total / area_m2, 2)
        }
    }
    
    return budget

if __name__ == "__main__":
    if len(sys.argv) < 4:
        # Fallback para pruebas manuales
        res = generate_budget(50000, 40000, 63)
    else:
        area = float(sys.argv[1])
        vol = float(sys.argv[2])
        cols = int(sys.argv[3])
        res = generate_budget(area, vol, cols)
    
    # Exportar el resultado a un JSON para que el orquestador lo lea
    with open("last_budget.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=4, ensure_ascii=False)
    
    print(f"Presupuesto generado exitosamente: ${res['resumen']['total_estimado']:,.2f} MXN")
