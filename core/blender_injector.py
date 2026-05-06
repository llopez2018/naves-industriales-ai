import urllib.request
import json
import sys
import os

def inject_to_blender(width, length, target_z):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    blender_script = os.path.join(base_dir, "..", "autocad", "generate_blender_twin.py").replace("\\", "/")

    blender_code = f"""
import sys
import importlib.util
spec = importlib.util.spec_from_file_location('gen', '{blender_script}')
m = importlib.util.module_from_spec(spec)
sys.modules['gen'] = m
spec.loader.exec_module(m)
m.generate_warehouse_twin({width}, {length}, {target_z})
"""

    payload = json.dumps({"code": blender_code}).encode('utf-8')
    url = "http://127.0.0.1:9876/execute"
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})

    try:
        # Timeout extendido para darle tiempo a bmesh de armar el terreno
        with urllib.request.urlopen(req, timeout=30.0) as response:
            if response.status == 200:
                print("> Ok: Inyeccion a Blender completada y dibujada.")
            else:
                print(f"> Error: Blender rechazo la inyeccion (Status {response.status}).")
    except Exception as e:
        print(f"> Aviso: Blender MCP se congelo o rechazo conexion. Detalle: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 3:
        w = sys.argv[1]
        l = sys.argv[2]
        z = sys.argv[3]
        inject_to_blender(w, l, z)
    else:
        print("> Error: Faltan argumentos.")
