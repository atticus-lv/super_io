import re
import urllib.request
import urllib.error
import json
import ssl
import bpy

from ..preferences import get_pref


def _parse_tag(tag: str) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    import re

    vers = tuple(
        tuple(int(x) for x in ver_str)
        for ver_str in
        [re.sub(r"[^0-9]", " ", ver_raw).split() for ver_raw in tag.split("-")]
    )

    if len(vers) == 1:
        return vers[0], (0, 0, 0)

    return vers


from .. import bl_info

RELEASES_URL = 'https://api.github.com/repos/atticus-lv/super_io/releases?per_page=10'
ADDON_VERSION = bl_info.get('version')


def _update_check() -> None:
    prefs = get_pref()

    ssl_context = ssl.SSLContext()

    try:

        with urllib.request.urlopen(RELEASES_URL, context=ssl_context) as response:
            data = json.load(response)

            for release in data:
                # if release["prerelease"]:
                #     continue

                if not release["draft"]:
                    update_version, required_blender = _parse_tag(release["tag_name"])
                    print('tag_name',update_version)
                    if update_version > ADDON_VERSION:
                        if required_blender <= bpy.app.version:
                            break

            with urllib.request.urlopen(release["assets_url"], context=ssl_context) as response:
                data = json.load(response)

                for asset in data:
                    if re.match(r".+\d+.\d+.\d+.+", asset["name"]):
                        break

                prerelease_note = " (pre-release)" if release["prerelease"] else ""

    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        print(e)


class SPIO_check_update(bpy.types.Operator):
    bl_idname = 'spio.check_update'
    bl_label = 'Check Update'

    def execute(self,context):
        _update_check()
        return {'FINISHED'}

def register():
    bpy.utils.register_class(SPIO_check_update)


def unregister():
    bpy.utils.unregister_class(SPIO_check_update)