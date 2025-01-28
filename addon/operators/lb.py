import bpy
import blf
import bmesh

from bpy_extras.io_utils import ImportHelper
from ..utility.utility import *


class LB_OT_NewGeometry(bpy.types.Operator):
    bl_idname = "scene.lb_new_geometry"
    bl_label = "Level New Geometry"

    brush_type: bpy.props.StringProperty(name="brush_type", default='NONE')

    def execute(self, context):
        scn = bpy.context.scene.lb_SceneProperties
        bpy.ops.object.select_all(action='DESELECT')

        if self.brush_type == 'SECTOR':
            bpy.ops.mesh.primitive_plane_add(size=2)
        else:
            bpy.ops.mesh.primitive_cube_add(size=2)

        ob = bpy.context.active_object
        lb_ob = bpy.context.active_object.lb_ObjectProperties

        lb_ob.csg_operation = 'ADD'

        ob.display_type = 'WIRE'
        ob.name = self.brush_type
        ob.data.name = self.brush_type

        lb_ob.brush_type = self.brush_type
        lb_ob.csg_order = 0
        lb_ob.brush_auto_texture = True
        bpy.context.view_layer.objects.active = ob

        lb_ob.ceiling_height = 4
        lb_ob.floor_height = 0
        lb_ob.ceiling_texture_scale_offset = (1.0, 1.0, 0.0, 0.0)
        lb_ob.wall_texture_scale_offset = (1.0, 1.0, 0.0, 0.0)
        lb_ob.floor_texture_scale_offset = (1.0, 1.0, 0.0, 0.0)
        lb_ob.ceiling_texture_rotation = 0
        lb_ob.wall_texture_rotation = 0
        lb_ob.floor_texture_rotation = 0
        lb_ob.ceiling_texture = ""
        lb_ob.wall_texture = ""
        lb_ob.floor_texture = ""

        update_brush(ob)

        return {"FINISHED"}
    
class LB_OT_RipGeometry(bpy.types.Operator):
    bl_idname = "object.lb_rip_geometry"
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

class LB_OT_BuildMap(bpy.types.Operator):
    bl_idname = "scene.lb_build_map"
    bl_label = "Build Map"

    bool_op: bpy.props.StringProperty(
        name="bool_op",
        default="UNION"
    )

    def execute(self, context):
        scn = bpy.context.scene.lb_SceneProperties
        was_edit_mode = False
        old_active = bpy.context.active_object
        old_selected = bpy.context.selected_objects.copy()
        if bpy.context.mode == 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='OBJECT')
            was_edit_mode = True

        brush_dictionary_list = {}
        brush_orders_sorted_list = []

        level_map = create_new_boolean_object(scn, "LevelGeometry")
        level_map.data = bpy.data.meshes.new("LevelGeometryMesh")
        level_map.data.use_auto_smooth = scn.map_use_auto_smooth
        level_map.data.auto_smooth_angle = math.radians(scn.map_auto_smooth_angle)
        level_map.hide_select = True
        level_map.hide_set(False)

        visible_objects = bpy.context.scene.collection.all_objects
        for ob in visible_objects:

            if not ob:
                continue

            if ob != level_map and ob.brush_type != 'NONE':
                update_brush(ob)

                if brush_dictionary_list.get(ob.csg_order, None) == None:
                    brush_dictionary_list[ob.csg_order] = []

                if ob.csg_order not in brush_orders_sorted_list:
                    brush_orders_sorted_list.append(ob.csg_order)

                brush_dictionary_list[ob.csg_order].append(ob)

        brush_orders_sorted_list.sort()
        bpy.context.view_layer.objects.active = level_map

        name_index = 0
        for order in brush_orders_sorted_list:
            brush_list = brush_dictionary_list[order]
            for brush in brush_list:
                brush.name = brush.csg_operation + "[" + str(order) + "]" + str(name_index)
                name_index += 1
                bool_obj = build_bool_object(brush)
                if brush.brush_auto_texture:
                    auto_texture(bool_obj, brush)
                apply_csg(level_map, brush, bool_obj)

        remove_material(level_map)

        update_location_precision(level_map)

        if bpy.context.scene.map_flip_normals:
            flip_object_normals(level_map)

        # restore context
        bpy.ops.object.select_all(action='DESELECT')
        if old_active:
            old_active.select_set(True)
            bpy.context.view_layer.objects.active = old_active
        if was_edit_mode:
            bpy.ops.object.mode_set(mode='EDIT')
        for obj in old_selected:
            if obj:
                obj.select_set(True)

        # remove trash
        for o in bpy.data.objects:
            if o.users == 0:
                bpy.data.objects.remove(o)
        for m in bpy.data.meshes:
            if m.users == 0:
                bpy.data.meshes.remove(m)
        # for m in bpy.data.materials:
        #     if m.users == 0:
        #         bpy.data.materials.remove(m)

        return {"FINISHED"}
    
class LB_OT_OpenMaterial(bpy.types.Operator, ImportHelper):
    bl_idname = "scene.lb_open_material"
    bl_label = "Open Material"

    filter_glob: bpy.props.StringProperty(
        default='*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp',
        options={'HIDDEN'}
    )

    files: bpy.props.CollectionProperty(
        type=bpy.types.OperatorFileListElement,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    def execute(self, context):
        directory, fileNameExtension = os.path.split(self.filepath)

        # do it for all selected files/images
        for f in self.files:
            fileName, fileExtension = os.path.splitext(f.name)

            # new material or find it
            new_material_name = fileName
            new_material = bpy.data.materials.get(new_material_name)

            if new_material == None:
                new_material = bpy.data.materials.new(new_material_name)

            new_material.use_nodes = True
            new_material.preview_render_type = 'FLAT'

            # We clear it as we'll define it completely
            new_material.node_tree.links.clear()
            new_material.node_tree.nodes.clear()

            # create nodes
            bsdfNode = new_material.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
            outputNode = new_material.node_tree.nodes.new('ShaderNodeOutputMaterial')
            texImageNode = new_material.node_tree.nodes.new('ShaderNodeTexImage')
            texImageNode.name = fileName
            texImageNode.image = bpy.data.images.load(directory + "\\" + fileName + fileExtension, check_existing=True)

            # create node links
            new_material.node_tree.links.new(bsdfNode.outputs['BSDF'], outputNode.inputs['Surface'])
            new_material.node_tree.links.new(bsdfNode.inputs['Base Color'], texImageNode.outputs['Color'])

            # some params
            bsdfNode.inputs['Roughness'].default_value = 0
            bsdfNode.inputs['Specular'].default_value = 0

        return {"FINISHED"}