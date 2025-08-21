import bpy
from mathutils import Vector

def dividir_eje_x_en_n(obj, n, parentar=True, alinear_rotacion=True):
    if obj is None or n < 2:
        print("Selecciona un objeto y usa un valor de N >= 2")
        return [], []

    bbox = [v[:] for v in obj.bound_box]
    min_x = min(v[0] for v in bbox)
    max_x = max(v[0] for v in bbox)
    min_y = min(v[1] for v in bbox)
    max_y = max(v[1] for v in bbox)
    min_z = min(v[2] for v in bbox)
    max_z = max(v[2] for v in bbox)

    longitud_x = max_x - min_x
    paso = longitud_x / (n - 1)

    centro_y = (min_y + max_y) / 2
    centro_z = (min_z + max_z) / 2

    x_locales = [min_x + i * paso for i in range(n)]
    posiciones_locales = [Vector((x, centro_y, centro_z)) for x in x_locales]
    posiciones_globales = [obj.matrix_world @ pos for pos in posiciones_locales]

    for i, pos in enumerate(posiciones_globales):
        empty = bpy.data.objects.new(f"Div_X_{i+1}", None)
        empty.empty_display_size = 0.2
        empty.empty_display_type = 'ARROWS'
        empty.location = pos

        if alinear_rotacion:
            empty.rotation_euler = obj.rotation_euler  # Copia la rotación del objeto

        if parentar:
            empty.parent = obj

        bpy.context.collection.objects.link(empty)

    return x_locales, posiciones_globales


# ==== CONFIGURACIÓN ====
objeto = bpy.context.active_object
N = 20
parentar = True
alinear_rotacion = True

dividir_eje_x_en_n(objeto, N, parentar, alinear_rotacion)
