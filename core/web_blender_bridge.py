import urllib.request
import json
import sys

def run_bridge():
    # Leer el codigo de Blender desde la entrada estandar
    blender_code = sys.stdin.read()
    
    payload = json.dumps({"code": blender_code}).encode('utf-8')
    url = "http://127.0.0.1:9876/execute"
    
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = response.read().decode('utf-8')
            print(result)
    except Exception as e:
        print(f"BRIDGE_ERROR: {e}")

if __name__ == "__main__":
    run_bridge()
