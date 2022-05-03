import argparse
import bpy
import sys
from math import floor


def main(argv):
    WORLD, SOURCEPATH, BLENDEPATH, SIZE, OUTPATH = argv
    SIZE = int(SIZE)

    bpy.ops.wm.open_mainfile(filepath=BLENDEPATH)

    context = bpy.context
    scene = context.scene

    with bpy.data.libraries.load(SOURCEPATH, link=False) as (data_from, data_to):
        data_to.worlds = [WORLD]

    context.scene.world = bpy.data.worlds[WORLD]

    # Render
    r = scene.render
    r.image_settings.file_format = 'PNG'
    r.image_settings.color_mode = 'RGBA'
    r.image_settings.color_depth = '8'
    r.image_settings.compression = 15
    r.resolution_x = SIZE
    r.resolution_y = SIZE
    r.resolution_percentage = 100
    r.filepath = OUTPATH

    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    if "--" not in sys.argv:
        argv = []  # as if no args are passed
    else:
        argv = sys.argv[sys.argv.index("--") + 1:]  # get all args after "--"
    main(argv)
