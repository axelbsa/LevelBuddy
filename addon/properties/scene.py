import bpy
from bpy.props import IntProperty, BoolProperty, FloatProperty, StringProperty

class LB_SceneProperties(bpy.types.PropertyGroup):

    map_precision: IntProperty(
        name="Map Precision",
        default=3,
        min=0,
        max=6,
        description='Controls the rounding level of vertex precisions.  Lower numbers round to higher values.  A level of "1" would round 1.234 to 1.2 and a level of "2" would round to 1.23'
    )


    map_use_auto_smooth: BoolProperty(
        name="Map Auto smooth",
        description='Use auto smooth',
        default=True,
    )


    map_auto_smooth_angle: FloatProperty(
        name="Map Auto smooth angle",
        description='Auto smooth angle',
        default=30,
        min = 0,
        max = 180,
        step=1,
        precision=0,
    )


    map_flip_normals: BoolProperty(
        name="Map Flip Normals",
        description='Flip output map normals',
        default=True,
    )


    remove_material: StringProperty(
        name="Remove Material",
        description="when the map is built all faces with this material will be removed."
    )