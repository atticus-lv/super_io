# This module is basic on https://github.com/Yeetus3141/ImagePaste

from .utils import Process
from .utils import File


class WindowsClipboard():
    """A concrete implementation of Clipboard for Windows."""

    def __init__(self, file_urls: list[File] = None) -> None:
        self.file_urls = file_urls

    @classmethod
    def push(cls):
        """A class method for pushing images from the Windows Clipboard.

        Args:
            save_directory (str): A path to a directory to save the pushed images.

        Returns:
            WindowsClipboard: A WindowsClipboard instance, which contains status of
                operations under Report object and a list of File objects holding
                pushed images information.
        """
        file_script = (
            "$files = Get-Clipboard -Format FileDropList\n"
            "if ($files) { $files.fullname }"
        )

        process = Process.execute(cls.get_powershell_args(file_script))

        if process.stdout[0] != "":
            files = [File(filepath) for filepath in process.stdout]
            print(f"Pasted {len(files)} file_url files: {files}")
            return cls(files)

        return cls()

    @classmethod
    def pull(cls, file_path: str):
        """A class method for pulling images to the Windows Clipboard.

        Args:
            file_path (str): A path to an image to be pulled to the clipboard.

        Returns:
            WindowsClipboard: A WindowsClipboard instance, which contains status of
                operations under Report object and a list of one File object that holds
                information of the pulled image we put its path to the input.
        """
        script = (
            "Add-Type -Assembly System.Windows.Forms\n"
            "Add-Type -Assembly System.Drawing\n"
            f'$file_url = [Drawing.File]::FromFile("{file_path}")\n'
            "[Windows.Forms.Clipboard]::SetFile($file_url)"
        )
        process = Process.execute(cls.get_powershell_args(script))
        if process.stderr:
            return cls()
        image = File(file_path)
        return cls([image])

    @staticmethod
    def get_powershell_args(script: str) -> list[str]:
        """A static method to get PowerShell arguments from a script for a process.

        Args:
            script (str): A script to be executed.

        Returns:
            list[str]: A list of PowerShell arguments for operating a process.
        """
        POWERSHELL = [
            "powershell",
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
                "[System.Text.Encoding]::UTF8\n"
                "$PSDefaultParameterValues['*:Encoding'] = 'utf8'\n" + script
        )

        args = POWERSHELL + ["& { " + script + " }"]
        return args
