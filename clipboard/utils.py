# This module is basic on https://github.com/Yeetus3141/ImagePaste

from __future__ import annotations


class Process:
    """A helper class for executing a command line process."""

    def __init__(self) -> None:
        """Initialize a Process instance."""
        self.parameters = {
            "encoding": 'utf-8',
            "text": True,
        }
        self.stdout = None
        self.stderr = None
        self.returncode = None

    @classmethod
    def execute(
            cls,
            args: list[str],
            shell: bool = False,
            capture_output: bool = True,
            split: bool = True,
            outpath: str = None,
    ) -> Process:
        """Execute a command line process.

        Args:
            args (list[str]): The command line arguments to execute.
            shell (bool, optional): If True, execute the command line using the shell.
                Defaults to False.
            capture_output (bool, optional): If True, capture the output of the command
                line. Defaults to True.
            outpath (str, optional): The path to write the output to. If not provided,
                the output will be returned as a string. Defaults to None.
            split (bool, optional): If True, split the output `stderr` into a list of
                lines. If False, it will be returned as a single string. The `stderr`
                is passed without any modifications. Defaults to True.

        Returns:
            Process: A Process instance with the output of the command line.
        """
        from subprocess import (
            DEVNULL,
            PIPE,
            Popen,
            STDOUT,
        )

        def comunicate(parameters):
            popen = Popen(**parameters)
            stdout, stderr = popen.communicate()
            return popen, stdout, stderr

        process = cls()
        process.parameters.update(
            {
                "args": args,
                "shell": shell,
                "stdout": PIPE if capture_output else DEVNULL,
                "stderr": PIPE if capture_output else STDOUT,
            }
        )
        if outpath:
            with open(outpath, "w") as file:
                process.parameters.update({"stdout": file})
                popen, stdout, stderr = comunicate(process.parameters)
        else:
            popen, stdout, stderr = comunicate(process.parameters)

        # Postprocess output
        if capture_output:
            if not outpath:
                process.stdout = stdout.strip().split("\n") if split else stdout.strip()
            process.stderr = stderr.strip()
        process.returncode = popen.returncode
        return process


class File:
    """A class to represent an image file."""
    pasted_images = {}
    image_index = 0

    def __init__(self, filepath: str, pasted: bool = False) -> None:
        """Constructor for the File class.

        Args:
            filepath (str): The path to the image file.
            filename (str, optional): The name of the image file.
            pasted (bool, optional): Whether the image is pasted.
        """
        self.filepath = filepath
        if pasted:
            File.pasted_images[self.filepath] = self
            File.image_index += 1

    @property
    def filepath(self) -> str:
        """Get the path to the image file."""
        return self._filepath

    @filepath.setter
    def filepath(self, filepath: str) -> None:
        """Set the path to the image file.

        Args:
            filepath (str): The path to the image file.
        """
        from os.path import basename
        from os.path import dirname

        self._filepath = filepath
        self.filename = basename(filepath)
        self.filebase = dirname(filepath)

    def __repr__(self) -> str:
        """Return a string representation of the File class.

        Returns:
            str: A string representation of the File class.
        """
        return f"{self.filename}<{self.filepath}>"
