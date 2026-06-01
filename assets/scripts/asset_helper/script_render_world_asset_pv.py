import argparse
import bpy
import sys
from math import floor


def main(argv):
    WORLD, SOURCEPATH, BLENDEPATH, OUTPATH, SIZE, SAMPLES, DENOISE = argv
    # convert
    SIZE = int(SIZE)
    SAMPLES = int(SAMPLES)
    DENOISE = True if DENOISE == '1' else False

    bpy.ops.wm.open_mainfile(filepath=BLENDEPATH)

    context = bpy.context
    scene = context.scene

    scene.cycles.samples = SAMPLES
    scene.cycles.use_denoising = DENOISE

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
