import bpy
import os


output_path = r"C:\Users\txaume\Documents\GitHub\res"

# Asegurar que la carpeta existe
if not os.path.exists(output_path):
    os.makedirs(output_path)
    
# Asegurar que todas las colecciones y subcolecciones estén visibles en render
for collection in bpy.data.collections:
    collection.hide_render = False  # Hacer visibles todas las colecciones en render
    
# Filtrar las mallas con nombres tipo "mesh_0", "mesh_0.001", etc.
objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH' and obj.name.startswith("Mesh_")]

print("Mallas encontradas:", [obj.name for obj in objects])

# Desactivar la visibilidad de todas las mallas en el render
for obj in objects:
    obj.hide_render = True

# Renderizar cada malla individualmente
for i, obj in enumerate(objects):
    obj.hide_render = False  # Mostrar solo este objeto
    bpy.context.view_layer.update()  # Actualizar la escena

    # Nombre del archivo (ejemplo: render_mesh_0.png, render_mesh_0_001.png)
    filename = f"render2_{obj.name}.png"
    filepath = os.path.join(output_path, filename)

    bpy.context.scene.render.filepath = filepath  # Asignar la ruta del render
    bpy.ops.render.render(write_still=True)  # Renderizar y guardar la imagen

    obj.hide_render = True  # Ocultar después de renderizar

# Restaurar visibilidad de todas las mallas al final
for obj in objects:
    obj.hide_render = False

print("Renderizado de objetos completado.")
