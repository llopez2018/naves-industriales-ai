import pythoncom
import win32com.client
import sys
import os

def load_xyz(filepath):
    """Lee el archivo del dron para AutoCAD"""
    puntos = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith("#"): continue
            p = line.split()
            if len(p) >= 3:
                puntos.append((float(p[0]), float(p[1]), float(p[2])))
    return puntos

def draw_nave_3d(width, length, target_z):
    try:
        acad = win32com.client.Dispatch("AutoCAD.Application")
        doc = acad.ActiveDocument
        ms = doc.ModelSpace
        
        print("Limpiando AutoCAD...")
        for i in range(ms.Count - 1, -1, -1):
            try: ms.Item(i).Delete()
            except: pass
        
        def aPnt(x, y, z=0):
            return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (float(x), float(y), float(z)))

        # Capas
        layers = doc.Layers
        def ensure_layer(name, color):
            try: layer = layers.Item(name)
            except: layer = layers.Add(name)
            layer.color = color
            return layer

        ensure_layer("3D_TERRENO", 52) 
        ensure_layer("3D_MUROS", 7)
        ensure_layer("3D_COLUMNAS", 1)
        ensure_layer("3D_PISO", 8)

        # 1. GENERAR TOPOGRAFÍA REAL DEL DRON
        print("Dibujando Nube de Puntos del Dron como Malla 3D...")
        xyz_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "core", "terreno_real_dron.xyz")
        
        # Para AutoCAD, crearemos caras 3D aproximadas basadas en los puntos para no saturarlo
        puntos = load_xyz(xyz_file)
        
        # Diccionario para acceso rápido a alturas Z basado en (X, Y)
        # El Dron se voló a resolución de 5m
        z_dict = {}
        for p in puntos:
            z_dict[(int(p[0]), int(p[1]))] = p[2]
            
        # Generar caras de 15x15m (submuestreo para que AutoCAD no se trabe)
        grid = 15
        for x in range(0, 300-grid, grid):
            for y in range(0, 300-grid, grid):
                z1 = z_dict.get((x, y), 50)
                z2 = z_dict.get((x+grid, y), 50)
                z3 = z_dict.get((x+grid, y+grid), 50)
                z4 = z_dict.get((x, y+grid), 50)
                
                face = ms.Add3DFace(aPnt(x, y, z1), aPnt(x+grid, y, z2), aPnt(x+grid, y+grid, z3), aPnt(x, y+grid, z4))
                face.Layer = "3D_TERRENO"

        # 2. GENERAR LA NAVE A COTA ÓPTIMA
        print(f"Dibujando Nave en Cota {target_z}m...")
        cx, cy = length/2, width/2
        
        # Piso (En la cota Z exacta)
        piso = ms.AddBox(aPnt(cx, cy, target_z - 0.5), length, width, 1)
        piso.Layer = "3D_PISO"

        # Muros
        ms.AddBox(aPnt(cx, 0, target_z + 5), length, 1, 10).Layer = "3D_MUROS"
        ms.AddBox(aPnt(cx, width, target_z + 5), length, 1, 10).Layer = "3D_MUROS"
        ms.AddBox(aPnt(0, cy, target_z + 5), 1, width, 10).Layer = "3D_MUROS"
        ms.AddBox(aPnt(length, cy, target_z + 5), 1, width, 10).Layer = "3D_MUROS"

        # Columnas
        for x in range(25, int(length), 25):
            for y in range(25, int(width), 25):
                c = ms.AddCylinder(aPnt(x, y, target_z + 5), 0.8, 10)
                c.Layer = "3D_COLUMNAS"

        doc.ActiveViewport.Direction = aPnt(1, -1, 1)
        doc.ActiveViewport = doc.ActiveViewport
        acad.ZoomExtents()
        print("AutoCAD terminado.")
        
    except Exception as e:
        print(f"Error en AutoCAD: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 3:
        w = float(sys.argv[1])
        l = float(sys.argv[2])
        z = float(sys.argv[3])
        draw_nave_3d(w, l, z)
    else:
        draw_nave_3d(200, 250, 60)
