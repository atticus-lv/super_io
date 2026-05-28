# log
# v0.1
# initial win
# v0.2
# add more ext support, add abc/usd node support
# v0.4
# read clipboard file paths with unicode Windows API

from __future__ import annotations

import sys
import ctypes
import ctypes.wintypes as w

import hou
import numpy as np

# change it to 'True' if your system encode if utf-8 (win)
FORCE_UNICORE = False

# Extension Config
ext_config = {
    'obj': 'file',
    'fbx': 'file',
    'stl': 'file',
    'dae': 'file',
    'abc': 'alembic',
    'usd': 'usdimport',
    'usda': 'usdimport',
    'usdc': 'usdimport',
}

# file node parm config
node_parm_config = {
    'file': 'file',
    'alembic': 'fileName',
    'usdimport': 'filepath1',
}


def main():
    if sys.platform != "win32":
        return print("Not Support this platform!")

    clipboard = WintypesClipboard()
    file_list = clipboard.pull(force_unicode=FORCE_UNICORE) or []
    del clipboard  # release clipboard

    if len(file_list) == 0:
        return print('No files found!')
    # remove extra files
    file_list = [file for file in file_list if file.split('.')[-1] in ext_config]

    # get context editor and mouse pos
    net_editor = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
    cursor_pos = net_editor.cursorPosition()

    # create or set nodes
    if len(hou.selectedNodes()) == 0:
        paneTabObj = hou.ui.paneTabUnderCursor()
        parent = paneTabObj.pwd()
        create_node_from_path_list(parent, file_list, cursor_pos)

    elif len(hou.selectedNodes()) == 1:
        node = hou.selectedNodes()[-1]

        set_node_path(node, file_list[0])
        file_list = file_list[1:]
        node.setSelected(True, clear_all_selected=True)

        parent = node.parent()

        create_node_from_path_list(parent, file_list, cursor_pos)


def create_node_from_path_list(obj, file_list, start_pos):
    for i, file in enumerate(file_list):
        node = obj.createNode(ext_config.get(file.split('.')[-1]))
        pos = np.subtract(start_pos, [-0.5, 1 * i])
        node.setPosition(pos)
        set_node_path(node, file)
        node.setSelected(True, clear_all_selected=True)


def set_node_path(node, path):
    for type, node_parm in node_parm_config.items():
        try:
            if node.type() == hou.sopNodeTypeCategory().nodeTypes()[type]:
                node.parm(node_parm).set(path)
                break
        except Exception:
            print(f'Config {type}:{node_parm} Error!')


class WintypesClipboard():
    def __init__(self, file_urls=None):
        # file_urls: list[str] = None
        self.file_urls = file_urls

        self.CF_HDROP = 15
        self.DRAG_QUERY_FILE_COUNT = 0xFFFFFFFF

        u32 = ctypes.windll.user32
        s32 = ctypes.windll.shell32

        self.OpenClipboard = u32.OpenClipboard
        self.OpenClipboard.argtypes = w.HWND,
        self.OpenClipboard.restype = w.BOOL

        self.GetClipboardData = u32.GetClipboardData
        self.GetClipboardData.argtypes = w.UINT,
        self.GetClipboardData.restype = w.HANDLE

        self.SetClipboardData = u32.SetClipboardData

        self.CloseClipboard = u32.CloseClipboard
        self.CloseClipboard.argtypes = None
        self.CloseClipboard.restype = w.BOOL

        self.DragQueryFile = s32.DragQueryFileW
        self.DragQueryFile.argtypes = [w.HANDLE, w.UINT, w.LPWSTR, w.UINT]
        self.DragQueryFile.restype = w.UINT

    def pull(self, force_unicode=False):
        self.file_urls = []

        opened = False
        try:
            if self.OpenClipboard(None):
                opened = True
                h_hdrop = self.GetClipboardData(self.CF_HDROP)

                if h_hdrop:
                    file_count = self.DragQueryFile(h_hdrop, self.DRAG_QUERY_FILE_COUNT, None, 0)

                    for index in range(file_count):
                        length = self.DragQueryFile(h_hdrop, index, None, 0)
                        if length == 0:
                            continue
                        buf = ctypes.create_unicode_buffer(length + 1)
                        self.DragQueryFile(h_hdrop, index, buf, length + 1)
                        self.file_urls.append(buf.value)

            return self.file_urls
        except (OSError, ctypes.ArgumentError):
            return []
        finally:
            if opened:
                self.CloseClipboard()


main()
