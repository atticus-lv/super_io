import sys
import ctypes
import ctypes.wintypes as w

from locale import getdefaultlocale

class DROPFILES(ctypes.Structure):
    _fields_ = (('pFiles', w.DWORD),
                ('pt',     w.POINT),
                ('fNC',    w.BOOL),
                ('fWide',  w.BOOL))

class WintypesClipboard():
    def __init__(self, file_urls = None):
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


    # def pull(self,file_list):
    #     offset = ctypes.sizeof(DROPFILES)
    #     length = sum(len(p) + 1 for p in file_list) + 1
    #     size = offset + length * ctypes.sizeof(ctypes.c_wchar)
    #     buf = (ctypes.c_char * size)()
    #     df = DROPFILES.from_buffer(buf)
    #     df.pFiles, df.fWide = offset, True
    #     for path in file_list:
    #         array_t = ctypes.c_wchar * (len(path) + 1)
    #         path_buf = array_t.from_buffer(buf, offset)
    #         path_buf.value = path
    #         offset += ctypes.sizeof(path_buf)
    #     stg = pythoncom.STGMEDIUM()
    #     stg.set(pythoncom.TYMED_HGLOBAL, buf)
    #     self.OpenClipboard()
    #     try:
    #         self.SetClipboardData(self.CF_HDROP,stg.data)
    #
    #     finally:
    #         self.CloseClipboard()

    def push(self,force_unicode = False):
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
