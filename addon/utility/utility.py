import bpy
import blf
import bmesh
import math

from copy import copy

from bpy_extras.io_utils import ImportHelper

csg_operation_to_blender_boolean = {
    "ADD": "UNION",
    "SUBTRACT": "DIFFERENCE"
}


def dump(obj):
    print("Properties in {}".format(str(obj)))
    for attr in dir(obj):
        print("obj.%s = %r" % (attr, getattr(obj, attr)))


def translate(val, t):
    return val + t


def scale(val, s):
    return val * s


def rotate2D(uv, degrees):
    radians = math.radians(degrees)
    newUV = copy(uv)
    newUV.x = uv.x*math.cos(radians) - uv.y*math.sin(radians)
    newUV.y = uv.x*math.sin(radians) + uv.y*math.cos(radians)
    return newUV


def auto_texture(bool_obj, source_obj):
    mesh = bool_obj.data
    objectLocation = source_obj.location
    objectScale = source_obj.scale

    lb_source_obj = source_obj.lb_ObjectProperties
    lb_bool_obj = bool_obj.lb_ObjectProperties

    bm = bmesh.new()
    bm.from_mesh(mesh)

    uv_layer = bm.loops.layers.uv.verify()
    for f in bm.faces:
        nX = f.normal.x
        nY = f.normal.y
        nZ = f.normal.z
        if nX < 0:
            nX = nX * -1
        if nY < 0:
            nY = nY * -1
        if nZ < 0:
            nZ = nZ * -1
        faceNormalLargest = nX
        faceDirection = "x"
        if faceNormalLargest < nY:
            faceNormalLargest = nY
            faceDirection = "y"
        if faceNormalLargest < nZ:
            faceNormalLargest = nZ
            faceDirection = "z"
        if faceDirection == "x":
            if f.normal.x < 0:
                faceDirection = "-x"
        if faceDirection == "y":
            if f.normal.y < 0:
                faceDirection = "-y"
        if faceDirection == "z":
            if f.normal.z < 0:
                faceDirection = "-z"
        for l in f.loops:
            luv = l[uv_layer]
            if faceDirection == "x":
                luv.uv.x = ((l.vert.co.y * objectScale[1]) + objectLocation[1])
                luv.uv.y = ((l.vert.co.z * objectScale[2]) + objectLocation[2])
                luv.uv = rotate2D(luv.uv, lb_source_obj.wall_texture_rotation)
                luv.uv.x =  translate(scale(luv.uv.x, lb_source_obj.wall_texture_scale_offset[0]), lb_source_obj.wall_texture_scale_offset[2])
                luv.uv.y =  translate(scale(luv.uv.y, lb_source_obj.wall_texture_scale_offset[1]), lb_source_obj.wall_texture_scale_offset[3])
            if faceDirection == "-x":
                luv.uv.x = ((l.vert.co.y * objectScale[1]) + objectLocation[1])
                luv.uv.y = ((l.vert.co.z * objectScale[2]) + objectLocation[2])
                luv.uv = rotate2D(luv.uv, lb_source_obj.wall_texture_rotation)
                luv.uv.x =  translate(scale(luv.uv.x, lb_source_obj.wall_texture_scale_offset[0]), lb_source_obj.wall_texture_scale_offset[2])
                luv.uv.y =  translate(scale(luv.uv.y, lb_source_obj.wall_texture_scale_offset[1]), lb_source_obj.wall_texture_scale_offset[3])
            if faceDirection == "y":
                luv.uv.x = ((l.vert.co.x * objectScale[0]) + objectLocation[0])
                luv.uv.y = ((l.vert.co.z * objectScale[2]) + objectLocation[2])
                luv.uv = rotate2D(luv.uv, lb_source_obj.wall_texture_rotation)
                luv.uv.x =  translate(scale(luv.uv.x, lb_source_obj.wall_texture_scale_offset[0]), lb_source_obj.wall_texture_scale_offset[2])
                luv.uv.y =  translate(scale(luv.uv.y, lb_source_obj.wall_texture_scale_offset[1]), lb_source_obj.wall_texture_scale_offset[3])
            if faceDirection == "-y":
                luv.uv.x = ((l.vert.co.x * objectScale[0]) + objectLocation[0])
                luv.uv.y = ((l.vert.co.z * objectScale[2]) + objectLocation[2])
                luv.uv = rotate2D(luv.uv, lb_source_obj.wall_texture_rotation)
                luv.uv.x =  translate(scale(luv.uv.x, lb_source_obj.wall_texture_scale_offset[0]), lb_source_obj.wall_texture_scale_offset[2])
                luv.uv.y =  translate(scale(luv.uv.y, lb_source_obj.wall_texture_scale_offset[1]), lb_source_obj.wall_texture_scale_offset[3])
            if faceDirection == "z":
                luv.uv.x = ((l.vert.co.x * objectScale[0]) + objectLocation[0])
                luv.uv.y = ((l.vert.co.y * objectScale[1]) + objectLocation[1])
                luv.uv = rotate2D(luv.uv, lb_source_obj.ceiling_texture_rotation)
                luv.uv.x =  translate(scale(luv.uv.x, lb_source_obj.ceiling_texture_scale_offset[0]), lb_source_obj.ceiling_texture_scale_offset[2])
                luv.uv.y =  translate(scale(luv.uv.y, lb_source_obj.ceiling_texture_scale_offset[1]), lb_source_obj.ceiling_texture_scale_offset[3])
            if faceDirection == "-z":
                luv.uv.x = ((l.vert.co.x * objectScale[0]) + objectLocation[0])
                luv.uv.y = ((l.vert.co.y * objectScale[1]) + objectLocation[1])
                luv.uv = rotate2D(luv.uv, lb_source_obj.floor_texture_rotation)
                luv.uv.x =  translate(scale(luv.uv.x, lb_source_obj.floor_texture_scale_offset[0]), lb_source_obj.floor_texture_scale_offset[2])
                luv.uv.y =  translate(scale(luv.uv.y, lb_source_obj.floor_texture_scale_offset[1]), lb_source_obj.floor_texture_scale_offset[3])
    bm.to_mesh(mesh)
    bm.free()

    bool_obj.data = mesh


def update_location_precision(ob):
    scn = bpy.context.scene.lb_SceneProperties
    ob.location.x = round(ob.location.x, scn.map_precision)
    ob.location.y = round(ob.location.y, scn.map_precision)
    ob.location.z = round(ob.location.z, scn.map_precision)
    cleanup_vertex_precision(ob)


def freeze_transforms(ob):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_pattern(pattern=ob.name)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.select_all(action='DESELECT')


def _update_sector_solidify(self, context):
    ob = context.active_object
    if ob.modifiers:
        mod = ob.modifiers[0]
        mod.thickness = ob.lb_ObjectProperties.ceiling_height - ob.lb_ObjectProperties.floor_height
        mod.offset = 1 + ob.lb_ObjectProperties.floor_height / (mod.thickness / 2)


def update_brush_sector_modifier(ob):
    if ob.lb_ObjectProperties.brush_type == 'BRUSH':
        for mod in ob.modifiers:
            if mod.type == 'SOLIDIFY':
                ob.modifiers.remove(mod)
        return

    has_solidify = False
    for mod in ob.modifiers:
        if mod.type == 'SOLIDIFY':
            has_solidify = True
            break
    
    if not has_solidify:
        bpy.ops.object.modifier_add(type='SOLIDIFY')

    for mod in ob.modifiers:
        if mod.type == 'SOLIDIFY':
            mod.use_even_offset = True
            mod.use_quality_normals = True
            mod.use_even_offset = True
            mod.thickness = ob.lb_ObjectProperties.ceiling_height - ob.lb_ObjectProperties.floor_height
            mod.offset = 1 + ob.lb_ObjectProperties.floor_height / (mod.thickness / 2)
            mod.material_offset = 1
            mod.material_offset_rim = 2
            break


def update_brush_sector_materials(ob):
    while len(ob.material_slots) < 3:
        bpy.ops.object.material_slot_add()
    while len(ob.material_slots) > 3:
        bpy.ops.object.material_slot_remove()

    if bpy.data.materials.find(ob.lb_ObjectProperties.ceiling_texture) != -1:
        ob.material_slots[0].material = bpy.data.materials[ob.lb_ObjectProperties.ceiling_texture]
    if bpy.data.materials.find(ob.lb_ObjectProperties.floor_texture) != -1:
        ob.material_slots[1].material = bpy.data.materials[ob.lb_ObjectProperties.floor_texture]
    if bpy.data.materials.find(ob.lb_ObjectProperties.wall_texture) != -1:
        ob.material_slots[2].material = bpy.data.materials[ob.lb_ObjectProperties.wall_texture]


# def update_brush_sector_materials(ob):
#     matCount = 0

#     ceilingMat = bpy.data.materials.find(ob.ceiling_texture) if ob.ceiling_texture != bpy.context.scene.remove_material else -1
#     floorMat = bpy.data.materials.find(ob.floor_texture) if ob.floor_texture != bpy.context.scene.remove_material else -1
#     wallMat = bpy.data.materials.find(ob.wall_texture) if ob.wall_texture != bpy.context.scene.remove_material else -1

#     if ceilingMat != -1:
#         matCount += 1
#     if floorMat != -1:
#         matCount += 1
#     if wallMat != -1:
#         matCount += 1

#     while len(ob.material_slots) < matCount:
#         bpy.ops.object.material_slot_add()
#     while len(ob.material_slots) > matCount:
#         bpy.ops.object.material_slot_remove()

#     matIndex = 0
#     if ceilingMat != -1:
#         ob.material_slots[matIndex].material = bpy.data.materials[ob.ceiling_texture]
#         matIndex += 1
#     if floorMat != -1:
#         ob.material_slots[matIndex].material = bpy.data.materials[ob.floor_texture]
#         matIndex += 1
#     if wallMat != -1:
#         ob.material_slots[matIndex].material = bpy.data.materials[ob.wall_texture]
#         matIndex += 1


def update_brush(obj):
    bpy.context.view_layer.objects.active = obj
    if obj:
        # while len(obj.modifiers) > 0:
        #     obj.modifiers.remove(obj.modifiers[0])

        obj.display_type = 'WIRE'

        update_brush_sector_modifier(obj)

        if obj.lb_ObjectProperties.brush_type == 'SECTOR':
            update_brush_sector_materials(obj)

        update_location_precision(obj)


def cleanup_vertex_precision(ob):
    scn = bpy.context.scene.lb_SceneProperties
    for v in ob.data.vertices:
        v.co.x = round(v.co.x, scn.map_precision)
        v.co.y = round(v.co.y, scn.map_precision)
        v.co.z = round(v.co.z, scn.map_precision)


def apply_csg(target, source_obj, bool_obj):
    bpy.ops.object.select_all(action='DESELECT')
    target.select_set(True)

    copy_materials(target, source_obj)

    lb_source_obj = source_obj.lb_ObjectProperties

    mod = target.modifiers.new(name=source_obj.name, type='BOOLEAN')
    mod.object = bool_obj
    mod.operation = csg_operation_to_blender_boolean[lb_source_obj.csg_operation]
    mod.solver = 'EXACT'
    bpy.ops.object.modifier_apply(modifier=source_obj.name)


def build_bool_object(sourceObj):
    bpy.ops.object.select_all(action='DESELECT')
    sourceObj.select_set(True)

    dg = bpy.context.evaluated_depsgraph_get()
    eval_obj = sourceObj.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(eval_obj)
    ob_bool = bpy.data.objects.new("_booley", me)
    copy_transforms(ob_bool, sourceObj)
    cleanup_vertex_precision(ob_bool)

    return ob_bool


def flip_object_normals(ob):
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.flip_normals()
    bpy.ops.object.mode_set(mode='OBJECT')


def create_new_boolean_object(scn, name):
    old_map = None
    if bpy.data.meshes.get(name + "_MESH") is not None:
        old_map = bpy.data.meshes[name + "_MESH"]
        old_map.name = "map_old"
    me = bpy.data.meshes.new(name + "_MESH")
    if bpy.data.objects.get(name) is None:
        ob = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(ob)
    else:
        ob = bpy.data.objects[name]
        ob.data = me
    if old_map is not None:
        bpy.data.meshes.remove(old_map)
    # bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    return ob


def copy_materials(target, source):
    if source.data == None:
        return
    if source.data.materials == None:
        return

    for sourceMaterial in source.data.materials:
        if sourceMaterial != None:
            if sourceMaterial.name not in target.data.materials:
                target.data.materials.append(sourceMaterial)


def copy_transforms(a, b):
    a.location = b.location
    a.scale = b.scale
    a.rotation_euler = b.rotation_euler


def remove_material(obj):
    scn = bpy.context.scene
    if scn.lb_SceneProperties.remove_material is not "":
        i = 0
        remove = False
        for m in obj.material_slots:
            if scn.lb_SceneProperties.remove_material == m.name:
                remove = True
            else:
                if not remove:
                    i += 1
        
        if remove:
            obj.active_material_index = i
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.material_slot_select()
            bpy.ops.mesh.delete(type='FACE')
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.material_slot_remove()


""" def update_sector_lighting(ob):
    mesh = ob.data; 
    color_layer = mesh.vertex_colors.active
    light_value = ob.sector_light_value
    light_type = 1.0
    if ob.sector_light_type == "NONE":
        light_type = 1.0
    if ob.sector_light_type == "PULSE":
        light_type = 0.0
    if ob.sector_light_type == "FLICKER":
        light_type = 0.1
    if ob.sector_light_type == "SWITCH 1":
        light_type = 0.2
    if ob.sector_light_type == "SWITCH 2":
        light_type = 0.3
    if ob.sector_light_type == "SWITCH 3":
        light_type = 0.4
    if ob.sector_light_type == "SWITCH 4":
        light_type = 0.5
    if ob.sector_light_type == "BLINK":
        light_type = 0.6
    light_max = ob.sector_light_max
    rgb = (light_value, light_type, light_max)
    if not mesh.vertex_colors:
        mesh.vertex_colors.new()
    for v in color_layer.data:
        v.color = rgb """
    # pass


def update_sector_lighting(ob):
    mesh = ob.data

    # Define the color attribute name
    color_attribute_name = "Col"

    # Create or get the color attribute
    if color_attribute_name not in mesh.color_attributes:
        color_attribute = mesh.color_attributes.new(name=color_attribute_name, type='FLOAT_COLOR', domain='CORNER')
    else:
        color_attribute = mesh.color_attributes[color_attribute_name]

    # Access the data of the attribute
    colors = color_attribute.data

    # Calculate light values
    light_value = ob.sector_light_value
    light_type = 1.0
    if ob.sector_light_type == "NONE":
        light_type = 1.0
    elif ob.sector_light_type == "PULSE":
        light_type = 0.0
    elif ob.sector_light_type == "FLICKER":
        light_type = 0.1
    elif ob.sector_light_type == "SWITCH 1":
        light_type = 0.2
    elif ob.sector_light_type == "SWITCH 2":
        light_type = 0.3
    elif ob.sector_light_type == "SWITCH 3":
        light_type = 0.4
    elif ob.sector_light_type == "SWITCH 4":
        light_type = 0.5
    elif ob.sector_light_type == "BLINK":
        light_type = 0.6

    light_max = ob.sector_light_max
    rgb = (light_value, light_type, light_max)

    # Set the color for each vertex corner (loop)
    for v in colors:
        v.color = (*rgb, 1.0)  # Add alpha channel if needed    
