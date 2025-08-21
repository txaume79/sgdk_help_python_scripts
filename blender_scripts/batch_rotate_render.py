
import bpy
import math
import os

# Nombres de objetos
MESH_NAME = "O0"
PLANE_NAME = "Plane"
CAMERA_NAME = "Camera"
RENDER_DIR = "//rotateds/"

# Crear carpeta de salida si no existe
output_path = bpy.path.abspath(RENDER_DIR)
os.makedirs(output_path, exist_ok=True)

# Obtener objetos
mesh = bpy.data.objects[MESH_NAME]
plane = bpy.data.objects[PLANE_NAME]
camera = bpy.data.objects[CAMERA_NAME]

# Guardar estado original
orig_mesh_loc = mesh.location.copy()
orig_mesh_rot = mesh.rotation_euler.copy()
orig_plane_loc = plane.location.copy()
orig_plane_rot = plane.rotation_euler.copy()
orig_camera_loc = camera.location.copy()
orig_camera_rot = camera.rotation_euler.copy()

# Obtener todos los empties
empties = [obj for obj in bpy.data.objects if obj.name.startswith("Div_X_")]

for i, empty in enumerate(sorted(empties, key=lambda e: e.location.x)):
    bpy.context.view_layer.objects.active = empty

    # 1. Cursor al empty
    bpy.context.scene.cursor.location = empty.location

    # 2. Mover plano a la X del empty (manteniendo Y y Z)
    plane.location.x = empty.location.x

    # 3. Mover cámara a la X del empty + 3, mantener Y y Z
    camera.location.x = empty.location.x + 3

    bpy.context.view_layer.update()

    # 4. Establecer origen del objeto y plano al cursor
    bpy.ops.object.select_all(action='DESELECT')
    mesh.select_set(True)
    bpy.context.view_layer.objects.active = mesh
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

    plane.select_set(True)
    bpy.context.view_layer.objects.active = plane
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

    # 5. Rotar y renderizar
    for angle_deg in range(45, -46, -10):
        angle_rad = math.radians(angle_deg)

        mesh.rotation_euler = (0, 0, angle_rad)
        plane.rotation_euler = (0, 0, angle_rad)
        bpy.context.view_layer.update()

        # Render ambos
        mesh.hide_render = False
        plane.hide_render = False
        bpy.context.scene.render.filepath = os.path.join(output_path+f"/{i}/", f"{i}_z{angle_deg:+03d}_both.png")
        bpy.ops.render.render(write_still=True)

        # Render solo mesh
        plane.hide_render = True
        bpy.context.view_layer.update()
        bpy.context.scene.render.filepath = os.path.join(output_path+f"/{i}/", f"{i}_z{angle_deg:+03d}_mesh_only.png")
        bpy.ops.render.render(write_still=True)
        plane.hide_render = False

    # 6. Restaurar origen de objeto y plano a su geometría
    for obj in [mesh, plane, camera]:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

    # 7. Restaurar posiciones y rotaciones originales
    mesh.location = orig_mesh_loc.copy()
    mesh.rotation_euler = orig_mesh_rot.copy()
    plane.location = orig_plane_loc.copy()
    plane.rotation_euler = orig_plane_rot.copy()
    camera.location = orig_camera_loc.copy()
    camera.rotation_euler = orig_camera_rot.copy()

    bpy.context.view_layer.update()
