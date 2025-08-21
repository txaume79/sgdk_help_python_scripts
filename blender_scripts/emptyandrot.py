bl_info = {
    "name": "Empty Rotation Renderer",
    "author": "ChatGPT",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Render Tools",
    "description": "Renderiza rotaciones de un objeto desde empties como centros",
    "category": "Render",
}

import bpy
import os
import math

class OBJECT_OT_render_from_empties(bpy.types.Operator):
    bl_idname = "object.render_from_empties"
    bl_label = "Render desde Empties"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        self.mesh = bpy.data.objects.get("O0")
        self.plane = bpy.data.objects.get("Plane")
        self.camera = bpy.data.objects.get("Camera")
        self.render_dir_base = bpy.path.abspath("//rotateds")
        self.original_mesh_rot =   self.mesh.rotation_euler.copy()
        self.original_plane_rot =  self.plane.rotation_euler.copy()
        self.mesh_x       =     self.mesh.location.x 
        self.mesh_y       =     self.mesh.location.y
        self.mesh_z       =     self.mesh.location.z
        self.plane_x      =     self.plane.location.x 
        self.plane_y      =     self.plane.location.y
        self.plane_z      =     self.plane.location.z
        self.camera_x     =     self.camera.location.x 
        self.camera_y     =     self.camera.location.y
        self.camera_z     =     self.camera.location.z  
        if not self.mesh or not self.plane or not self.camera:
            self.report({'ERROR'}, "No se encuentran O0, Plane o Camera")
            return {'CANCELLED'}
       
        for obj in [self.mesh, self.plane]:
            self.report({'INFO'}, "setting origin geometry for mesh and plane")
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

        self.report({'INFO'}, "backing up position and rotation")
        self.mesh.rotation_mode = 'XYZ'
        self.plane.rotation_mode = 'XYZ'


        self.report({'INFO'}, "getting all empties")     
        empties = [obj for obj in bpy.data.objects if obj.name.startswith("Div_X_")]
        empties.sort(key=lambda e: e.location.x)

        def render_sequence(self):
            for i, empty in enumerate(empties):
                bpy.context.scene.cursor.location = empty.location
                self.plane.location.x = empty.location.x
                self.camera.location.x = empty.location.x
                for obj in [mesh, plane]:
                    bpy.ops.object.select_all(action='DESELECT')
                    obj.select_set(True)
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

                self.report({'INFO'}, "starting render sequence")
                for angle_deg in range(45, -46, -10):
                    self.report({'INFO'}, "Angle ")
                    angle_rad = math.radians(angle_deg)
                    self.mesh.rotation_euler = (0, 0, angle_rad)
                    self.plane.rotation_euler = (0, 0, angle_rad)
                    bpy.context.view_layer.update()

                    self.mesh.hide_render = False
                    self.plane.hide_render = False
                    bpy.context.scene.render.filepath = os.path.join(self.output_path, f"z{angle_deg:+03d}_both.png")
                    bpy.ops.render.render(write_still=True)

                    self.plane.hide_render = True
                    bpy.context.view_layer.update()
                    bpy.context.scene.render.filepath = os.path.join(self.output_path, f"z{angle_deg:+03d}_mesh_only.png")
                    bpy.ops.render.render(write_still=True)
                    self.plane.hide_render = False
                    self.render_dir = os.path.join(self.render_dir_base, f"{i:02d}")
                    os.makedirs(self.render_dir, exist_ok=True)
                    for obj in [self.mesh, self.plane]:
                        bpy.ops.object.select_all(action='DESELECT')
                        obj.select_set(True)
                        bpy.context.view_layer.objects.active = obj
                        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

                    self.mesh.location.x   = self.mesh_x  
                    self.mesh.location.y   = self.mesh_y  
                    self.mesh.location.z   = self.mesh_z  
                    self.plane.location.x  = self.plane_x 
                    self.plane.location.y  = self.plane_y 
                    self.plane.location.z  = self.plane_z 
                    self.camera.location.x = self.camera_x
                    self.camera.location.y = self.camera_y
                    self.camera.location.z = self.camera_z
                    self.mesh.rotation_euler = self.original_mesh_rot.copy()
                    self.plane.rotation_euler = self.original_plane_rot.copy()
                    bpy.context.view_layer.update()


                    render_sequence(self)

                

        self.report({'INFO'}, "Renderizado completo")
        return {'FINISHED'}

class VIEW3D_PT_render_tools(bpy.types.Panel):
    bl_label = "Render Tools"
    bl_idname = "VIEW3D_PT_render_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Render Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.render_from_empties")

def register():
    bpy.utils.register_class(OBJECT_OT_render_from_empties)
    bpy.utils.register_class(VIEW3D_PT_render_tools)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_render_from_empties)
    bpy.utils.unregister_class(VIEW3D_PT_render_tools)

if __name__ == "__main__":
    register()
