#!/bin/bash

function cleanup(){
     rm -rf test_script.py
}

# Configuration
BLENDER_PATH="/home/axl/.local/share/Steam/steamapps/common/Blender/blender-launcher"  # Adjust this path to your blender executable
ADDON_NAME="LevelBuddy"
ADDON_PATH="/home/axl/src/python/LevelBuddy"
BLENDER_SCRIPTS_PATH="$HOME/.config/blender/4.3/scripts"
ADDON_SYMLINK="$BLENDER_SCRIPTS_PATH/addons/$ADDON_NAME"

# Create necessary directories
mkdir -p "$BLENDER_SCRIPTS_PATH/addons"

# Create symlink if it doesn't exist
if [ ! -L "$ADDON_SYMLINK" ]; then
    ln -s "$ADDON_PATH" "$ADDON_SYMLINK"
fi

# Create a temporary loader script
LOADER_SCRIPT=$(mktemp)
cat > "$LOADER_SCRIPT" << 'EOF'
import bpy
import sys
import os

# Get the addon name from environment variable
addon_name = os.environ.get('BLENDER_ADDON_NAME')
addon_path = os.environ.get('BLENDER_ADDON_PATH')

# Ensure the addon directory is in the Python path
if addon_path not in sys.path:
    sys.path.append(os.path.dirname(addon_path))

# First, try to remove the addon if it's already registered
try:
    bpy.ops.preferences.addon_disable(module=addon_name)
except:
    pass

# Remove the module if it's already loaded
if addon_name in sys.modules:
    del sys.modules[addon_name]
    # Also remove submodules
    for k in list(sys.modules.keys()):
        if k.startswith(addon_name + '.'):
            del sys.modules[k]

# Enable the addon
bpy.ops.preferences.addon_enable(module=addon_name)
EOF

# Launch Blender with our loader script
BLENDER_ADDON_NAME="$ADDON_NAME" BLENDER_ADDON_PATH="$ADDON_PATH" "$BLENDER_PATH" \
    --python-exit-code 1 \
    --python "$LOADER_SCRIPT" \
    "$@"

# Clean up
rm "$LOADER_SCRIPT"
