import bpy
from bpy.props import (IntProperty, BoolProperty, FloatProperty, StringProperty,
                       FloatVectorProperty, EnumProperty)

from ..utility.utility import _update_sector_solidify


class LB_ObjectProperties(bpy.types.PropertyGroup):
    ceiling_texture_scale_offset: FloatVectorProperty(
        name="Ceiling Texture Scale Offset",
        default=(1, 1, 0, 0),
        min=0,
        step=10,
        precision=3,
        size=4
    )

    wall_texture_scale_offset: FloatVectorProperty(
        name="Wall Texture Scale Offset",
        default=(1, 1, 0, 0),
        min=0,
        step=10,
        precision=3,
        size=4
    )

    floor_texture_scale_offset: FloatVectorProperty(
        name="Floor Texture Scale Offset",
        default=(1, 1, 0, 0),
        min=0,
        step=10,
        precision=3,
        size=4
    )

    ceiling_texture_rotation: FloatProperty(
        name="Ceiling Texture Rotation",
        default=0,
        min=0,
        step=10,
        precision=3,
    )

    wall_texture_rotation: FloatProperty(
        name="Wall Texture Rotation",
        default=0,
        min=0,
        step=10,
        precision=3,
    )

    floor_texture_rotation: FloatProperty(
        name="Floor Texture Rotation",
        default=0,
        min=0,
        step=10,
        precision=3,
    )

    ceiling_height: FloatProperty(
        name="Ceiling Height",
        default=4,
        step=10,
        precision=3,
        update=_update_sector_solidify
    )

    floor_height: FloatProperty(
        name="Floor Height",
        default=0,
        step=10,
        precision=3,
        update=_update_sector_solidify
    )

    floor_texture: StringProperty(
        name="Floor Texture",
    )

    wall_texture: StringProperty(
        name="Wall Texture",
    )

    ceiling_texture: StringProperty(
        name="Ceiling Texture",
    )

    brush_type: EnumProperty(
        items=[
            ("BRUSH", "Brush", "is a brush"),
            ("SECTOR", "Sector", "is a sector"),
            ("NONE", "None", "none"),
        ],
        name="Brush Type",
        description="the brush type",
        default='NONE'
    )

    csg_operation: EnumProperty(
        items=[
            ("ADD", "Add", "add/union geometry to output"),
            ("SUBTRACT", "Subtract", "subtract/remove geometry from output"),
        ],
        name="CSG Operation",
        description="the CSG operation",
        default='ADD'
    )

    csg_operation_to_blender_boolean = {
        "ADD": "UNION",
        "SUBTRACT": "DIFFERENCE"
    }

    csg_order: IntProperty(
        name="CSG Order",
        default=0,
        description='Controls the order of CSG operation of the object'
    )

    brush_auto_texture: BoolProperty(
        name="Brush Auto Texture",
        default=True,
        description='Auto Texture on or off'
    )