from __future__ import annotations

import subprocess
import os
import sys
import ctypes
import ctypes.wintypes as w

from locale import getdefaultlocale


class Clipboard():
    def __init__(self, file_urls=None):
        if sys.platform not in {'win32', 'darwin'}:
            raise EnvironmentError

    def pull_files_from_clipboard(self, force_unicode):
        file_list = []

        if sys.platform == 'win32':
            clipboard = WinTypeClipboard()
            file_list = clipboard.pull(force_unicode)

            del clipboard

            if file_list is None:
                clipboard = PowerShellClipboard()
                file_list = clipboard.pull()

        elif sys.platform == 'darwin':
            clipboard = MacClipboard()
            file_list = clipboard.pull()

        return file_list

    def push_to_clipboard(self, paths):
        if sys.platform == 'win32':
            clipboard = PowerShellClipboard()
        elif sys.platform == 'darwin':
            clipboard = MacClipboard()

        clipboard.push_to_clipboard(paths)

    def push_pixel_to_clipboard(self, path):
        if sys.platform == 'win32':
            clipboard = PowerShellClipboard()
        elif sys.platform == 'darwin':
            clipboard = MacClipboard()

        clipboard.push_pixel_to_clipboard(path)


class MacClipboard():

    def pull(self, force_unicode=False):
        self.file_urls = []
        from .darwin import _native as pasteboard

        pb = pasteboard.Pasteboard()

        urls = pb.get_file_urls()

        if urls is not None:
            self.file_urls = list(urls)

        return self.file_urls

    def push_pixel_to_clipboard(self, path):
        commands = [
            "set the clipboard to "
            f'(read file POSIX file "{path}" as «class PNGf»)'
        ]

        subprocess.Popen(self.get_osascript_args(commands))

    def push_to_clipboard(self, paths):
        commands = [
            "set the clipboard to "
            f'(POSIX file "{paths[0]}")'
        ]

        subprocess.Popen(self.get_osascript_args(commands))

    def get_osascript_args(self, commands):
        args = ["osascript"]
        for command in commands:
            args += ["-e", command]
        return args


class PowerShellClipboard:
    def get_args(self, script):
        powershell_args = [
            os.path.join(
                os.getenv("SystemRoot"),
                "System32",
                "WindowsPowerShell",
                "v1.0",
                "powershell.exe",
            ),
            "-NoProfile",
            "-NoLogo",
            "-NonInteractive",
            "-WindowStyle",
            "Hidden",
        ]
        script = (
                "$OutputEncoding = "
                "[System.Console]::OutputEncoding = "
                "[System.Console]::InputEncoding = "
                "[System.Text.Encoding]::UTF8; "
                + "$PSDefaultParameterValues['*:Encoding'] = 'utf8'; "
                + script
        )
        args = powershell_args + ["& { " + script + " }"]
        return args

    def push_pixel_to_clipboard(self, path):
        script = (
            "Add-Type -Assembly System.Windows.Forms; "
            "Add-Type -Assembly System.Drawing; "
            f"$image = [Drawing.Image]::FromFile('{path}'); "
            "$imageStream = New-Object System.IO.MemoryStream; "
            "$image.Save($imageStream, [System.Drawing.Imaging.ImageFormat]::Png); "
            "$dataObj = New-Object System.Windows.Forms.DataObject('Bitmap', $image); "
            "$dataObj.SetData('PNG', $imageStream); "
            "[System.Windows.Forms.Clipboard]::SetDataObject($dataObj, $true); "
        )

        self.execute_powershell(script)

    def push_to_clipboard(self, paths):
        join_s = ""

        for path in paths:
            join_s += f", '{path}'"

        script = (
            f"$filelist = {join_s};"
            "$col = New-Object Collections.Specialized.StringCollection; "
            "foreach($file in $filelist){$col.add($file)}; "
            "Add-Type -Assembly System.Windows.Forms; "
            "[System.Windows.Forms.Clipboard]::SetFileDropList($col); "
        )

        self.execute_powershell(script)

    def pull(self):
        script = (
            "Add-Type -AssemblyName System.Windows.Forms; "
            "$files = Get-Clipboard -Format FileDropList; "
            "if ($files) { $files.fullname }"
        )

        popen, stdout, stderr = self.execute_powershell(script)

        self.file_urls = stdout.split('\n')
        self.file_urls[:] = [file for file in self.file_urls if file != '']

        return self.file_urls

    def execute_powershell(self, script):
        parms = {
            'args': self.get_args(script),
            'encoding': 'utf-8',
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
        }
        popen = subprocess.Popen(**parms)
        stdout, stderr = popen.communicate()
        return popen, stdout, stderr


class WinTypeClipboard:
    def __init__(self):
        self.file_urls = []

        self.CF_HDROP = 15

        u32 = ctypes.windll.user32
        k32 = ctypes.windll.kernel32
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

        self.DragQueryFile = s32.DragQueryFile
        self.DragQueryFile.argtypes = [w.HANDLE, w.UINT, ctypes.c_void_p, w.UINT]

    @property
    def file_list(self):
        return self.file_urls

    def pull(self, force_unicode=False):
        # get
        try:
            if self.OpenClipboard(None):
                h_hdrop = self.GetClipboardData(self.CF_HDROP)

                if h_hdrop:
                    # expose force unicode to preferences(if enabled unicode beta setting)
                    FS_ENCODING = getdefaultlocale()[1] if not force_unicode else 'utf-8'
                    file_count = self.DragQueryFile(h_hdrop, -1, None, 0)

                    for index in range(file_count):
                        buf = ctypes.c_buffer(260)
                        self.DragQueryFile(h_hdrop, index, buf, ctypes.sizeof(buf))
                        self.file_urls.append(buf.value.decode(FS_ENCODING))

            return self.file_urls
        except UnicodeError:
            pass
        finally:
            self.CloseClipboard()
