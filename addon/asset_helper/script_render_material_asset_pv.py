import argparse
import bpy
import sys
import os
from math import floor


def main(argv):
    MAT, SOURCEPATH, BLENDEPATH, OUTPATH, SIZE, SAMPLES, DENOISE, DISPLACE = argv
    # convert
    SIZE = int(SIZE)
    SAMPLES = int(SAMPLES)
    DENOISE = True if DENOISE == '1' else False
    DISPLACE = True if DISPLACE == '1' else False

    bpy.ops.wm.open_mainfile(filepath=BLENDEPATH)

    context = bpy.context
    scene = context.scene

    scene.cycles.samples = SAMPLES
    scene.cycles.use_denoising = DENOISE

    # there is some bug with the api now
    with bpy.data.libraries.load(SOURCEPATH, link=False) as (data_from, data_to):
        data_to.materials = [MAT]

    bpy.data.objects['SHADERBALL'].material_slots[0].material = bpy.data.materials.get(MAT)

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

    if DISPLACE:
        scene.cycles.feature_set = 'EXPERIMENTAL'
        scene.cycles.dicing_rate = 2
        scene.cycles.preview_dicing_rate = 2
        mod = bpy.data.objects['SHADERBALL'].modifiers.new('Subdivision', 'SUBSURF')
        mod.levels = 1
        mod.render_levels = 1
        bpy.context.object.modifiers["Subdivision"].subdivision_type = 'CATMULL_CLARK'
        bpy.data.objects['SHADERBALL'].cycles.use_adaptive_subdivision = True

    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    if "--" not in sys.argv:
        argv = []  # as if no args are passed
    else:
        argv = sys.argv[sys.argv.index("--") + 1:]  # get all args after "--"
    main(argv)
