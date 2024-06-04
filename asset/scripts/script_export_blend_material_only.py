import argparse
import bpy
import sys


def main(args):
    print("Script args: ", args)

    if len(args) > 0:
        parser = argparse.ArgumentParser()
        parser.add_argument('blend')
        parser.add_argument('--pack', action='append')
        args = parser.parse_args(args)

        blend = args.blend

        print(f"Blend to fix: {blend}")

        bpy.ops.wm.open_mainfile(filepath=blend)

        # pack
        bpy.ops.file.pack_all()
        try:
            bpy.ops.file.pack_libraries()
        except Exception as e:
            print(e)

        for o in bpy.data.objects:
            bpy.data.objects.remove(o)

        bpy.context.view_layer.update()
        bpy.context.preferences.filepaths.save_version = 0  # No backup blends needed
        bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True)


if __name__ == "__main__":
    if "--" not in sys.argv:
        argv = []  # as if no args are passed
    else:
        argv = sys.argv[sys.argv.index("--") + 1:]  # get all args after "--"
    main(argv)
