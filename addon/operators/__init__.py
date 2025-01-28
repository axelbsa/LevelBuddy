import bpy
from bpy.utils import register_class, unregister_class
from . import lb

classes = [
    lb.LB_OT_NewGeometry,
    lb.LB_OT_RipGeometry,
    lb.LB_OT_BuildMap,
    lb.LB_OT_OpenMaterial,
]

def register():
    for cls in classes:
        register_class(cls)
        
def unregister():
    for cls in classes:
        unregister_class(cls)