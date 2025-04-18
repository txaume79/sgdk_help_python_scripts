import bpy
import bmesh
import mathutils
# bpy.ops.wm.console_toggle()

# Note from the verbose author TheNomCognom 18/04/2025
# This script gets a blender model and bisects on n parts. Use as you wish.
def getObjectSizeOnAxis(objname, axis):

    # axis equivalence (0 = X, 1 = Y, 2 = Z)
    max_vertex = [0,0,0]
    min_vertex = [0,0,0]

    obj = bpy.data.objects[objname]
    obj_mesh = obj.data


    # Apply vertex transformations
    world_vertices = [obj.matrix_world @ v.co for v in obj_mesh.vertices]

    # find extrem vertex on selected axis
    min_vertex = min(world_vertices, key=lambda v: v[axis])
    max_vertex = max(world_vertices, key=lambda v: v[axis])

    return [min_vertex, max_vertex]

# axis will be always x
def placeSegPlanes(numofsegments, maxminvertex):
    
    vertex = [0,0,0]    
    nueva_coleccion = bpy.data.collections.new("SegPlanesCollection")
    bpy.context.scene.collection.children.link(nueva_coleccion)
    positionalvertex = list(maxminvertex[0]) 
    if maxminvertex[0][0] < 0: 
       segmentsize = (maxminvertex[1][0] + abs(maxminvertex[0][0])) / (numofsegments -1)
    else: 
       segmentsize = (maxminvertex[1][0] - abs(maxminvertex[0][0])) / (numofsegments -1)

    print(segmentsize)
    for i in range(1, numofsegments-1):
        positionalvertex[0] += segmentsize
        bpy.ops.mesh.primitive_plane_add(size=2, location=positionalvertex)
        
        plane = bpy.context.object
        plane.name = "PlanoSeg_"+str(i)
        plane.rotation_euler = (0,1.571 ,0)

        
        
def knifeObjectBisect(object_to_cut, numofsegments):
    obj = bpy.data.objects[object_to_cut]
    
    for i in range(1,numofsegments-1):
        bpy.ops.object.select_all(action='DESELECT')
        plano = bpy.data.objects['PlanoSeg_'+str(i)] # TODO bucle

        punto_plano = plano.location
        normal_plano = plano.matrix_world.to_3x3() @ mathutils.Vector((0, 0, 1))

        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects[obj.name].select_set(True)

        bpy.context.view_layer.objects.active = bpy.data.objects[obj.name]
       
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)

        edges = []

        ret = bmesh.ops.bisect_plane(bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:], plane_co=punto_plano, plane_no=normal_plano)
        bmesh.ops.split_edges(bm, edges=[e for e in ret['geom_cut'] if isinstance(e, bmesh.types.BMEdge)])

        bmesh.update_edit_mesh(obj.data)

        bpy.ops.mesh.separate(type='LOOSE')
        bpy.ops.object.mode_set(mode='OBJECT')
        
        copia = obj.copy()
        copia.name = object_to_cut + "_segment_" + str(i)
        
        
def removePlaneRefs(numofsegments):
    for i in range(1, numofsegments-1):
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects['PlanoSeg_'+str(i)].select_set(True)
        bpy.ops.object.delete(confirm=True)

if __name__ == "__main__":
    # objeto is the name of the object you want to be sliced
    objeto = 'O0'
    # getObjectSizeOnAxis(objectname, axis) -> axis equivalence (0 = X, 1 = Y, 2 = Z)
    maxminvertex=getObjectSizeOnAxis(objeto,0)

    # placeSegPlanes(num of slices, vertex douple) places the planes that will be used to bisect
    placeSegPlanes(9, maxminvertex)

    # knifeObjectBisect(objectname, num of slices) bisects the object in 9 parts
    knifeObjectBisect(objeto,9)

    # as i need a reference plane i do the same for them
    planoref = 'P0'
    knifeObjectBisect(planoref,9)
    planoref = 'P0.001'
    knifeObjectBisect(planoref,9)
    removePlaneRefs(9)