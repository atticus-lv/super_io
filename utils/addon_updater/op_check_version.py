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

from ...preferences import get_pref
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

            for release in data:
                if not release["draft"]:
                    update_version = _parse_tag(release["tag_name"])[0]
                    print(update_version)
                    if update_version >= ADDON_VERSION:
                        break

            with urllib.request.urlopen(release["assets_url"], context=ssl_context) as response:
                data = json.load(response)

                for asset in data:
                    if re.match(r".+\d+.\d+.\d+.+", asset["name"]):
                        break

                prerelease_note = " (pre-release)" if release["prerelease"] else ""

                state.update_available = True
                state.update_version = ".".join(str(x) for x in update_version) + prerelease_note
                state.download_url = asset["browser_download_url"]
                state.changelog_url = release["html_url"]

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

    def draw(self, context):
        layout = self.layout

        layout.label(text=f'Current Version: {".".join(str(x) for x in ADDON_VERSION)}')
        if state.status == state.CHECKING:
            layout.label(text='Checking...')
        elif state.status == state.COMPLETED:
            if state.update_available is True:
                layout.label(text=f'Latest Version: {state.update_version}')
                row = layout.row()
                row.operator('wm.url_open', text='Download', icon='URL').url = state.download_url
                row.operator('wm.url_open', text='Change Log', icon='URL').url = state.changelog_url
            elif state.update_available is False:
                layout.label(text="You've installed the latest version")
        else:
            if state.error_msg:
                layout.label(text=state.error_msg)

    def invoke(self, context, event):
        state.update_available = state.update_version = state.download_url = state.changelog_url = state.error_msg = None

        threading.Thread(target=_update_check, args=()).start()
        if state.error_msg is not None:
            return {'CANCELLED'}

        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        return {'FINISHED'}


def register():
    bpy.utils.register_class(SPIO_check_update)


def unregister():
    bpy.utils.unregister_class(SPIO_check_update)
