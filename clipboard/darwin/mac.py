from __future__ import annotations

import sys
import subprocess

class MacClipboard():
    def __init__(self, file_urls = None):
        # file_urls: list[str] = None
        self.file_urls = file_urls

    def pull(self, force_unicode=False):
        self.file_urls = []
        from .pasteboard import _native as pasteboard

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

    def push_to_clipboard(self,paths):
        join_s = ''
        for path in paths:
            join_s+=f'(POSIX file "{path}"),'
        if join_s.endswith(','): join_s = join_s[:-1]
        command = [
        f'set f to {{join_s}}'
        'tell application "Finder'
            'try -- to delete any old temp folder'
                'delete folder "SPIO_Copy" of (path to temporary items)'
            'end try'
            'set tmp to make new folder at (path to temporary items) with properties {name:"SPIO_Copy"}'
            'duplicate f to tmp'
            'select files of tmp'
            'activate'
            'tell application "System Events" to keystroke "c" using command down'
            'delete tmp'
        'end tell'
        ]

        subprocess.Popen(self.get_osascript_args(command))


    def get_osascript_args(self,commands):
        args = ["osascript"]
        for command in commands:
            args += ["-e", command]
        return args