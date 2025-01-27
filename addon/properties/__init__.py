import bpy
from bpy.utils import register_class, unregister_class
from . import scene, object


classes = [
    scene.LB_SceneProperties,
    object.LB_ObjectProperties,

]

def register():
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.TLM_SceneProperties = bpy.props.PointerProperty(type=scene.LB_SceneProperties)
    bpy.types.Object.TLM_ObjectProperties = bpy.props.PointerProperty(type=object.LB_ObjectProperties)
  

def unregister():
    for cls in classes:
        unregister_class(cls)

    del bpy.types.Scene.LB_SceneProperties
    del bpy.types.Object.LB_ObjectProperties
