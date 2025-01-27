import bpy, os
from bpy.utils import register_class, unregister_class
from . import panels

classes = [
    panels.LB_MainPanel
]

def register():
    for cls in classes:
        register_class(cls)

def unregister():
    for cls in classes:
        unregister_class(cls)