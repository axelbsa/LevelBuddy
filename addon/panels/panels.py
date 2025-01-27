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