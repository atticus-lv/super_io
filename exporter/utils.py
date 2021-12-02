import subprocess
import os
import bpy

def execute(cmd):
    """
    Runs an external application, in this case the blender executable for
    thumbnail generation.
    Returns the object to watch for completion.
    """
    return subprocess.Popen(cmd, universal_newlines=True)


def execute_blender(args):
    """
    Execute Blender with given arguments.
    Returns the object to watch for completion.
    """
    args.insert(0, bpy.app.binary_path)
    print(" ".join(args))
    return execute(args)


def run_blend_fix(asset):
    """
    Fixes the given .blend file, by instancing all objects in the active scene.
    """
    args = [
        "--background",
        "--factory-startup",
        "--python",
        os.path.join(os.path.dirname(__file__), "fix_blend.py"),
        "--",
        asset,
    ]

    # for p in pack:
    #     args.append("--pack")
    #     args.append(p)

    execute_blender(args).wait()  # Wait for completion.
