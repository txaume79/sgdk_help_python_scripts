import bpy
import math
import os

# Configuración
MESH_NAME = "Mesh_0"
PLANE_NAME = "Plane"
CAMERA_NAME = "Camera"
RENDER_DIR = "//renders"

# Obtener los objetos
mesh = bpy.data.objects.get(MESH_NAME)
plane = bpy.data.objects.get(PLANE_NAME)
camera = bpy.data.objects.get(CAMERA_NAME)

if not mesh or not plane or not camera:
    raise Exception("No se encontraron uno o más objetos: Mesh_0, Plane o Camera.")

# Asegurar modo de rotación en Euler XYZ
mesh.rotation_mode = 'XYZ'
plane.rotation_mode = 'XYZ'

# Crear carpeta de salida si no existe
output_path = bpy.path.abspath(RENDER_DIR)
os.makedirs(output_path, exist_ok=True)

# Rotar en eje Z desde 45 hasta -45 en pasos de 10
for angle_deg in range(45, -46, -10):
    angle_rad = math.radians(angle_deg)

    # Aplicar rotación Z
    mesh.rotation_euler = (0, 0, angle_rad)
    plane.rotation_euler = (1.570, 0, angle_rad)

    bpy.context.view_layer.update()

    # Render con ambos objetos
    mesh.hide_render = False
    plane.hide_render = False

    bpy.context.scene.render.filepath = os.path.join(
        output_path, f"z{angle_deg:+03d}_both.png"
    )
    bpy.ops.render.render(write_still=True)

    # Render solo Mesh_0
    plane.hide_render = True
    bpy.context.view_layer.update()

    bpy.context.scene.render.filepath = os.path.join(
        output_path, f"z{angle_deg:+03d}_mesh_only.png"
    )
    bpy.ops.render.render(write_still=True)

    # Restaurar visibilidad
    plane.hide_render = False
