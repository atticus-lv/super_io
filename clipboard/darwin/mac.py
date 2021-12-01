from __future__ import annotations

import sys
from locale import getdefaultlocale


class MacClipboard():
    def __init__(self, file_urls = None):
        # file_urls: list[str] = None
        self.file_urls = file_urls

    def push(self, force_unicode=False):
        self.file_urls = []
        from .pasteboard import _native as pasteboard

        pb = pasteboard.Pasteboard()

        urls = pb.get_file_urls()

        if urls is not None:
            self.file_urls = list(urls)

        return self.file_urls
