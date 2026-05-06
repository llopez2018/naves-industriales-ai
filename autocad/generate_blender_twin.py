import bpy
import bmesh
import sys
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

def generate_warehouse_twin(width, length, target_z):
    print("Iniciando Generacion en Blender...")
    
    # 1. Limpiar Escena de forma segura
    for obj in bpy.context.scene.objects:
        obj.select_set(True)
    bpy.ops.object.delete()

    print("Generando Terreno Real Dron (Optimizado)...")
    xyz_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "core", "terreno_real_dron.xyz")
    
    if os.path.exists(xyz_file):
        puntos = load_xyz(xyz_file)
        
        # 2. Generar malla usando bmesh (mucho mas rapido y no congela Blender)
        mesh = bpy.data.meshes.new("Malla_Terreno")
        bm = bmesh.new()
        
        # Crear vertices
        bm_verts = []
        for p in puntos:
            bm_verts.append(bm.verts.new(p))
            
        bm.verts.ensure_lookup_table()
        
        # Crear caras (Grid 5m, 300x300)
        grid_size = 5 
        cols = 300 // grid_size
        rows = 300 // grid_size
        
        for y in range(rows - 1):
            for x in range(cols - 1):
                i = y * cols + x
                try:
                    # Crear cara con 4 vertices
                    bm.faces.new((bm_verts[i], bm_verts[i+1], bm_verts[i+cols+1], bm_verts[i+cols]))
                except:
                    pass # Ignorar caras invalidas
                    
        bm.to_mesh(mesh)
        bm.free()
        
        terreno = bpy.data.objects.new("Superficie_Terreno", mesh)
        bpy.context.collection.objects.link(terreno)
        
        # Material Tierra
        mat_tierra = bpy.data.materials.new(name="Tierra")
        mat_tierra.use_nodes = True
        mat_tierra.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.3, 0.2, 0.1, 1)
        terreno.data.materials.append(mat_tierra)
    else:
        print("Aviso: No hay archivo XYZ. Generando piso plano.")

    print("Generando Nave Industrial...")
    cx, cy = length/2, width/2

    # Piso
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, target_z - 1))
    piso = bpy.context.active_object
    piso.scale = (length, width, 2)
    
    # Muros
    def add_wall(name, loc, sca):
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
        wall = bpy.context.active_object
        wall.scale = sca

    add_wall("Muro_N", (cx, width, target_z + 5), (length, 0.2, 10))
    add_wall("Muro_S", (cx, 0, target_z + 5), (length, 0.2, 10))
    add_wall("Muro_E", (length, cy, target_z + 5), (0.2, width, 10))
    add_wall("Muro_O", (0, cy, target_z + 5), (0.2, width, 10))

    # Luz y Camara
    bpy.ops.object.light_add(type='SUN', location=(cx, cy, target_z + 100))
    bpy.context.active_object.data.energy = 5

    bpy.ops.object.camera_add(location=(length*1.5, -width*0.5, target_z + 80))
    cam = bpy.context.active_object
    cam.rotation_euler = (1.0, 0, 0.8)
    bpy.context.scene.camera = cam
    
    # Forzar actualizacion visual inmediata
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    
    print("PROCESO_COMPLETADO")

if __name__ == "__main__":
    try:
        idx = sys.argv.index("--")
        w = float(sys.argv[idx + 1])
        l = float(sys.argv[idx + 2])
        z = float(sys.argv[idx + 3])
    except:
        w, l, z = 200, 250, 60
        
    generate_warehouse_twin(w, l, z)
