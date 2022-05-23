import re
import os
import urllib.request
import urllib.error
import json
import bpy
import io
import pathlib
import zipfile
import urllib.request
import urllib.error
import shutil
import ssl

from ...preferences.prefs import get_pref
from ... import __folder_name__
from ... import bl_info
from . import state

ADDON_VERSION = bl_info.get('version')
RELEASES_URL = 'https://api.github.com/repos/atticus-lv/super_io/releases?per_page=10'


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


def _update_check() -> None:
    ssl_context = ssl.SSLContext()
    state.status = state.CHECKING
    # redraw
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()
    try:

        with urllib.request.urlopen(RELEASES_URL, context=ssl_context) as response:
            data = json.load(response)

            newest_version = None

            for i, release in enumerate(data):
                if release["draft"]: continue

                update_version = _parse_tag(release["tag_name"])[0]
                if newest_version is None: newest_version = update_version
                break
                # if update_version >= ADDON_VERSION and i == 1:
                #     break

            if update_version is None:
                state.status = state.ERROR
                state.error_msg = 'No update available (Network error or using a dev version)'

            with urllib.request.urlopen(release["assets_url"], context=ssl_context) as response:
                data = json.load(response)

                links = list()
                names = list()

                for asset in data:
                    # if re.match(r".+\d+.\d+.\d+.+", asset["name"]):
                    links.append(asset["browser_download_url"])
                    names.append(asset["name"])

                prerelease_note = " (pre-release)" if release["prerelease"] else ""

                state.update_available = True
                state.update_version = ".".join(str(x) for x in update_version) + prerelease_note
                state.download_url = links
                state.download_name = names
                state.changelog = release["body"].split('\r\n')
                print(state.changelog)

        state.status = state.COMPLETED
        # redraw
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                area.tag_redraw()

    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        state.error_msg = str(e)


import threading


class SPIO_check_update(bpy.types.Operator):
    bl_idname = 'spio.check_update'
    bl_label = 'Check Update'

    @staticmethod
    def draw_update(layout):
        layout.box().label(text=f'Current Version: {".".join(str(x) for x in ADDON_VERSION)}', icon='BLENDER')
        if state.status == state.CHECKING:
            layout.box().label(text='Checking...', icon='VIEWZOOM')
        elif state.status == state.COMPLETED:
            if state.update_available is True:
                col = layout.column()

                box = col.box().column(align=True)
                box.label(text=f'Latest Version: {state.update_version}', icon='ERROR')
                for line in state.changelog:
                    if line.startswith('+'):
                        box.label(text=line.replace('+', ''), icon='KEYFRAME')
                    elif line.startswith('    +'):
                        row = box.row(align = True)
                        row.separator(factor = 2)
                        row.label(text=line.replace('    +', ''), icon='DOT')
                    else:
                        box.label(text=line)

                box = col.box().column(align=False)
                box.label(text='Download', icon='IMPORT')
                for i, url in enumerate(state.download_url):
                    text = state.download_name[i]
                    col.operator('wm.url_open', text=text).url = url

            elif state.update_available is False:
                layout.label(text="You've installed the latest version")
        else:
            if state.error_msg:
                layout.label(text=state.error_msg)

    def execute(self, context):
        state.update_available = state.update_version = state.download_url = state.changelog = state.error_msg = None

        threading.Thread(target=_update_check, args=()).start()
        if state.error_msg is not None:
            return {'CANCELLED'}

        return {'FINISHED'}


def register():
    bpy.utils.register_class(SPIO_check_update)


def unregister():
    bpy.utils.unregister_class(SPIO_check_update)
