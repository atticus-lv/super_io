import sys
import ctypes
import ctypes.wintypes as w

from locale import getdefaultlocale


class DROPFILES(ctypes.Structure):
    _fields_ = (('pFiles', w.DWORD),
                ('x', w.LONG),
                ('y', w.LONG),
                ('fNC', w.BOOL),
                ('fWide', w.BOOL))


pDropFiles = DROPFILES()
pDropFiles.pFiles = ctypes.sizeof(DROPFILES)
pDropFiles.fWide = True
metadata = bytes(pDropFiles)


class WintypesClipboard():
    def __init__(self, file_urls=None):
        # file_urls: list[str] = None
        self.file_urls = file_urls

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

    def pull(self, file_list):
        files = ('\0'.join(file_list)).replace('/', '\\')
        data = files.encode('U16')[2:] + b'\0\0'

        if self.OpenClipboard(None):
            try:
                self.SetClipboardData(self.CF_HDROP, metadata + data)
            except Exception as e:
                print(e)
            finally:
                self.CloseClipboard()

    def push(self, force_unicode=False):
        self.file_urls = []

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

        self.CloseClipboard()
        return self.file_urls
