import argparse
import bpy
import sys
from math import floor


def main(argv):
    FILEPATH,OUTPATH, SIZE_X, SCALE, COLORSPACE = argv
    SIZE_X = int(SIZE_X)
    SCALE = float(SCALE)

    context = bpy.context
    scene = context.scene

    scene.use_nodes = True
    node_tree = scene.node_tree

    # Remove default nodes, except composite
    n_comp = None
    for n in node_tree.nodes:
        if not n.type == 'COMPOSITE':
            node_tree.nodes.remove(n)
        else:
            n_comp = n

    img = bpy.data.images.load(FILEPATH)
    n_img = node_tree.nodes.new("CompositorNodeImage")
    n_img.image = img

    n_blur = node_tree.nodes.new("CompositorNodeBlur")
    n_blur.filter_type = 'FLAT'
    n_blur.size_x = floor(img.size[0] / SIZE_X / 2)
    n_blur.size_y = n_blur.size_x

    n_scale = node_tree.nodes.new("CompositorNodeScale")
    n_scale.space = "RENDER_SIZE"
    n_scale.frame_method = "CROP"

    # Links
    links = node_tree.links
    links.new(n_img.outputs[0], n_blur.inputs[0])
    links.new(n_blur.outputs[0], n_scale.inputs[0])
    links.new(n_scale.outputs[0], n_comp.inputs[0])

    # Render
    r = scene.render
    r.image_settings.file_format = 'JPEG'
    r.image_settings.quality = 95
    r.resolution_x = SIZE_X
    r.resolution_y = int(SIZE_X / SCALE)
    r.resolution_percentage = 100
    r.filepath = OUTPATH
    scene.view_settings.view_transform = COLORSPACE

    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    if "--" not in sys.argv:
        argv = []  # as if no args are passed
    else:
        argv = sys.argv[sys.argv.index("--") + 1:]  # get all args after "--"
    main(argv)
