import bpy
from mathutils import Vector

# Paso 1: Aplicar todas las transformaciones
def apply_all_transforms(obj):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Paso 2: Obtener el bounding box verdadero del objeto
def get_true_bounding_box(obj):
    # Obtención de la caja delimitadora (bounding box) del objeto
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()

    # Calcular las coordenadas del bounding box usando el objeto transformado
    coords_world = [obj.matrix_world @ v.co for v in mesh.vertices]
    min_corner = Vector((min(v[i] for v in coords_world) for i in range(3)))
    max_corner = Vector((max(v[i] for v in coords_world) for i in range(3)))

    eval_obj.to_mesh_clear()
    return min_corner, max_corner

# Paso 3: Crear un cubo que circunscriba el objeto
def create_bounding_cube(obj, cube_name, collection, margen=0.05):
    min_corner, max_corner = get_true_bounding_box(obj)
    size = max_corner - min_corner
    center = (min_corner + max_corner) / 2

    # Aplicar un margen al cubo
    size_with_margin = size * (1.0 + margen)

    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    cube = bpy.context.object
    cube.name = cube_name
    cube.scale = size_with_margin  # Aquí ya no dividimos entre 2

    # Aplicar transformaciones
    bpy.ops.object.transform_apply(scale=True)

    # Añadir el cubo a la colección
    collection.objects.link(cube)
    bpy.context.collection.objects.unlink(cube)

    return cube

# Paso 4: Crear la colección de modificadores
def create_modifiers_collection():
    if "modifiers" in bpy.data.collections:
        return bpy.data.collections["modifiers"]
    else:
        new_col = bpy.data.collections.new("modifiers")
        bpy.context.scene.collection.children.link(new_col)
        return new_col

# Paso 5: Duplicar objetos y asociar cubos
def duplicate_and_process_object(obj_name, n_copies, separation, margen=0.05):
    original = bpy.data.objects.get(obj_name)
    if not original:
        print(f"Objeto '{obj_name}' no encontrado.")
        return

    apply_all_transforms(original)
    modifiers_collection = create_modifiers_collection()

    for i in range(n_copies):
        # Crear una copia del objeto
        obj_copy = original.copy()
        obj_copy.data = original.data.copy()
        obj_copy.name = f"{original.name}.{str(i).zfill(3)}"
        obj_copy.location = original.location + Vector((i * separation, 0, 0))

        bpy.context.collection.objects.link(obj_copy)

        # Crear el cubo circunscrito
        cube_name = f"Cube_{obj_copy.name}"
        cube = create_bounding_cube(obj_copy, cube_name, modifiers_collection, margen=margen)

        # Añadir el modificador Mesh Deform al objeto
        modifier = obj_copy.modifiers.new(name="MeshDeform", type='MESH_DEFORM')
        # modifier.object = cube
        
        copy = obj_copy.modifiers["MeshDeform"].object = cube
        # bpy.ops.object.meshdeform_bind(modifier=modifier.name)
        
        #override = {"object": obj_copy, "active_object": obj_copy, "scene":bpy.data.scenes['Scene'] }
        
        
        area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
        override = bpy.context.copy()
        override['area'] = area
        override['region'] = next(region for region in area.regions if region.type == 'WINDOW')
        override['active_object'] = obj_copy
        override['object'] = obj_copy
        
        
        
        with bpy.context.temp_override(**override):
            bpy.ops.object.meshdeform_bind(modifier=modifier.name) 



# --- PARÁMETROS ---
nombre_objeto = "Mesh_0"     # Nombre del objeto base
numero_copias = 5            # Número de copias
separacion_x = 3            # Distancia en el eje X entre copias
margen_extra = 0.05          # 5% extra en tamaño del cubo

duplicate_and_process_object(nombre_objeto, numero_copias, separacion_x, margen=margen_extra)


