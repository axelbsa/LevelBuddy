import bpy, blf, bmesh

class LB_PT_MainPanel(bpy.types.Panel):
    bl_label = "Level Buddy"
    bl_idname = "LB_PT_MainPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = 'UI'
    bl_category = 'Level Buddy'

    def draw(self, context):
        ob = context.active_object
        scn = bpy.context.scene
        layout = self.layout
        col = layout.column(align=True)
        col.label(icon="WORLD", text="Map Settings")
        col.prop(scn, "map_flip_normals")
        col.prop(scn, "map_precision")
        col.prop(scn, "map_use_auto_smooth")
        col.prop(scn, "map_auto_smooth_angle")
        col.prop_search(scn, "remove_material", bpy.data, "materials")
        col = layout.column(align=True)
        col.operator("scene.level_buddy_build_map", text="Build Map", icon="MOD_BUILD").bool_op = "UNION"
        col.operator("scene.level_buddy_open_material", text="Open Material", icon="TEXTURE")
        col = layout.column(align=True)
        col.label(icon="SNAP_PEEL_OBJECT", text="Tools")
        if bpy.context.mode == 'EDIT_MESH':
            col.operator("object.level_rip_geometry", text="Rip", icon="UNLINKED").remove_geometry = True
        else:
            col.operator("scene.level_buddy_new_geometry", text="New Sector", icon="MESH_PLANE").brush_type = 'SECTOR'
            col.operator("scene.level_buddy_new_geometry", text="New Brush", icon="CUBE").brush_type = 'BRUSH'
        if ob is not None and len(bpy.context.selected_objects) > 0:
            col = layout.column(align=True)
            col.label(icon="MOD_ARRAY", text="Brush Properties")
            col.prop(ob, "brush_type", text="Brush Type")
            col.prop(ob, "csg_operation", text="CSG Op")
            col.prop(ob, "csg_order", text="CSG Order")
            col.prop(ob, "brush_auto_texture", text="Auto Texture")
            if ob.brush_auto_texture:
                col = layout.row(align=True)
                col.prop(ob, "ceiling_texture_scale_offset")
                col = layout.row(align=True)
                col.prop(ob, "wall_texture_scale_offset")
                col = layout.row(align=True)
                col.prop(ob, "floor_texture_scale_offset")
                col = layout.row(align=True)
                col.prop(ob, "ceiling_texture_rotation")
                col = layout.row(align=True)
                col.prop(ob, "wall_texture_rotation")
                col = layout.row(align=True)
                col.prop(ob, "floor_texture_rotation")
            if ob.brush_type == 'SECTOR' and ob.modifiers:
                col = layout.column(align=True)
                col.label(icon="MOD_ARRAY", text="Sector Properties")
                col.prop(ob, "ceiling_height")
                col.prop(ob, "floor_height")
                # layout.separator()
                col = layout.column(align=True)
                col.prop_search(ob, "ceiling_texture", bpy.data, "materials", icon="MATERIAL", text="Ceiling")
                col.prop_search(ob, "wall_texture", bpy.data, "materials", icon="MATERIAL", text="Wall")
                col.prop_search(ob, "floor_texture", bpy.data, "materials", icon="MATERIAL", text="Floor")


class LB_OT_NewGeometry(bpy.types.Operator):
    bl_idname = "LB_OT_new_geometry"
    bl_label = "Level New Geometry"

    brush_type: bpy.props.StringProperty(name="brush_type", default='NONE')

    def execute(self, context):
        scn = bpy.context.scene
        bpy.ops.object.select_all(action='DESELECT')

        if self.brush_type == 'SECTOR':
            bpy.ops.mesh.primitive_plane_add(size=2)
        else:
            bpy.ops.mesh.primitive_cube_add(size=2)

        ob = bpy.context.active_object

        ob.csg_operation = 'ADD'

        ob.display_type = 'WIRE'
        ob.name = self.brush_type
        ob.data.name = self.brush_type
        ob.brush_type = self.brush_type
        ob.csg_order = 0
        ob.brush_auto_texture = True
        bpy.context.view_layer.objects.active = ob

        ob.ceiling_height = 4
        ob.floor_height = 0
        ob.ceiling_texture_scale_offset = (1.0, 1.0, 0.0, 0.0)
        ob.wall_texture_scale_offset = (1.0, 1.0, 0.0, 0.0)
        ob.floor_texture_scale_offset = (1.0, 1.0, 0.0, 0.0)
        ob.ceiling_texture_rotation = 0
        ob.wall_texture_rotation = 0
        ob.floor_texture_rotation = 0
        ob.ceiling_texture = ""
        ob.wall_texture = ""
        ob.floor_texture = ""

        update_brush(ob)

        return {"FINISHED"}
    
class LB_PT_RipGeometry(bpy.types.Operator):
    bl_idname = "object.level_rip_geometry"
    bl_label = "Level Rip Sector"

    remove_geometry: bpy.props.BoolProperty(name="remove_geometry", default=False)

    def execute(self, context):
        active_obj = bpy.context.active_object

        active_obj_bm = bmesh.from_edit_mesh(active_obj.data)
        riped_obj_bm = bmesh.new()

        # https://blender.stackexchange.com/questions/179667/split-off-bmesh-selected-faces
        active_obj_bm.verts.ensure_lookup_table()
        active_obj_bm.edges.ensure_lookup_table()
        active_obj_bm.faces.ensure_lookup_table()

        selected_faces = [x for x in active_obj_bm.faces if x.select]
        selected_edges = [x for x in active_obj_bm.edges if x.select]

        py_verts = []
        py_edges = []
        py_faces = []

        # rip geometry
        if len(selected_faces) > 0:
            for f in selected_faces:
                cur_face_indices = []
                for v in f.verts:
                    if v not in py_verts:
                        py_verts.append(v)
                    cur_face_indices.append(py_verts.index(v))

                py_faces.append(cur_face_indices)
        elif len(selected_edges) > 0:
            for e in selected_edges:
                if e.verts[0] not in py_verts:
                    py_verts.append(e.verts[0])
                if e.verts[1] not in py_verts:
                    py_verts.append(e.verts[1])

                vIndex0 = py_verts.index(e.verts[0])
                vIndex1 = py_verts.index(e.verts[1])

                py_edges.append([vIndex0, vIndex1])
        else:
            # early out
            riped_obj_bm.free()
            return {"CANCELLED"}

        # remove riped
        if active_obj.brush_type != 'BRUSH' and self.remove_geometry and len(selected_faces) > 0:
            edges_to_remove = []
            for f in selected_faces:
                for e in f.edges:
                    if e not in edges_to_remove:
                        edges_to_remove.append(e)

            for f in selected_faces:
                active_obj_bm.faces.remove(f)

            for e in edges_to_remove:
                if e.is_wire:
                    active_obj_bm.edges.remove(e)

        active_obj_bm.verts.ensure_lookup_table()
        active_obj_bm.edges.ensure_lookup_table()
        active_obj_bm.faces.ensure_lookup_table()

        # create mesh
        riped_mesh = bpy.data.meshes.new(name='riped_mesh')
        mat = active_obj.matrix_world
        if len(py_faces) > 0:
            riped_mesh.from_pydata([x.co for x in py_verts], [], py_faces)
        else:
            riped_mesh.from_pydata([x.co for x in py_verts], py_edges, [])

        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        riped_obj = active_obj.copy()
        for coll in active_obj.users_collection:
            coll.objects.link(riped_obj)
        riped_obj.data = riped_mesh
        copy_materials(riped_obj, active_obj)

        riped_obj.select_set(True)
        bpy.context.view_layer.objects.active = riped_obj
        bpy.ops.object.mode_set(mode='EDIT')

        bpy.ops.mesh.select_all(action='SELECT')

        riped_obj_bm.free()

        return {"FINISHED"}