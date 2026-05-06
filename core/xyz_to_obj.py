import os

def load_xyz(filepath):
    puntos = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith("#"): continue
            p = line.split()
            if len(p) >= 3:
                puntos.append((float(p[0]), float(p[1]), float(p[2])))
    return puntos

def export_obj_from_xyz(xyz_file, obj_file):
    print(f"Convirtiendo {xyz_file} a Malla 3D ({obj_file})...")
    puntos = load_xyz(xyz_file)
    
    if not puntos:
        return False
        
    grid_size = 5 
    cols = 300 // grid_size
    rows = 300 // grid_size
    
    with open(obj_file, 'w') as f:
        f.write("# Terreno Dron exportado para Blender MCP\n")
        
        # 1. Escribir vertices (v x y z)
        for p in puntos:
            f.write(f"v {p[0]:.3f} {p[1]:.3f} {p[2]:.3f}\n")
            
        # 2. Escribir caras (f v1 v2 v3 v4) - Los indices en OBJ empiezan en 1
        for y in range(rows - 1):
            for x in range(cols - 1):
                i = y * cols + x + 1 # +1 porque OBJ es 1-based
                # Cara con 4 vertices: i, i+1, i+cols+1, i+cols
                f.write(f"f {i} {i+1} {i+cols+1} {i+cols}\n")
                
    print(f"Exportacion OBJ completada: {len(puntos)} vertices.")
    return True

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    xyz = os.path.join(base_dir, "terreno_real_dron.xyz")
    obj = os.path.join(base_dir, "terreno_real_dron.obj")
    export_obj_from_xyz(xyz, obj)
