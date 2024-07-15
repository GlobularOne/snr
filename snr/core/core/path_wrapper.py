"""
Wrap os and shutil functions around a specific path
"""

import os
import os.path
import shutil
from types import TracebackType
from typing import IO, Any

__all__ = (
    "PathWrapperBase",
)


class PathWrapperBase:
    """
    Base class for wrapping os and shutil functions around a specific path
    """
    _path_var_name: str

    def __init__(self, path: str):
        self._path = path
        self._path_var_name = "_path"

    def __init_subclass__(cls, path_var_name: str) -> None:
        cls._path_var_name = path_var_name

    def _get_path(self) -> str:
        return getattr(self, self._path_var_name) # type: ignore 

    def join(self, *paths: str) -> str:
        """Join paths with the wrapped path

        Returns:
            Absolute path
        """
        return os.path.join(self._get_path(), *paths)

    def dirname(self, path: str) -> str:
        """Return directory name (parent) of path, inside the wrapped path

        Args:
            path: Path to work on 

        Returns:
            Parent of path as it would be inside the wrapped path, to get the absolute path of that
            use join on it.
        """
        # Special case: Call dirname without joining
        # Otherwise we would create absolute paths that cannot
        # be used with the rest of the functions in this class
        return os.path.dirname(path)

    def exists(self, path: str) -> bool:
        """Check if the specified path exists inside the wrapped path

        Args:
            path: Path to work on 

        Returns:
            Whatever it exists or not
        """
        return os.path.exists(self.join(path))

    def isdir(self, path: str) -> bool:
        """Check if the specified path is a directory or not

        Args:
            path: Path to work on

        Returns:
            Whatever it is a directory or not
        """
        return os.path.isdir(self.join(path))

    def isfile(self, path: str) -> bool:
        """Check if the specified path is a file or not

        Args:
            path: Path to work on

        Returns:
            Whatever it is a file or not
        """
        return os.path.isfile(self.join(path))

    def islink(self, path: str) -> bool:
        """Check if the specified path is a link or not

        Args:
            path: Path to work on

        Returns:
            Whatever it is a link or not
        """
        return os.path.islink(self.join(path))

    def open(self, file: str, mode: str = "r", buffering: int = -1, encoding: str | None = None) -> IO[Any]:
        """Open a file in the wrapped directory

        Args:
            file: The name of the file to open.
            mode: The mode to open the file in.
            buffering: The buffering size in bytes.
            encoding: The encoding to use.

        Returns:
            file-like object
        """
        stream = open(self.join(file), mode, buffering,  # pylint: disable=consider-using-with
                      encoding)

        def __enter__() -> IO[Any]:  # pylint: disable=unused-variable
            return stream.__enter__()

        def __exit__(exc_type: type[BaseException] | None,  # pylint: disable=unused-variable
                     exc_val: BaseException | None,
                     exc_tb: TracebackType | None) -> None:  # pylint: disable=unused-variable
            return stream.__exit__(exc_type, exc_val, exc_tb)
        return stream

    def remove(self, path: str) -> None:
        """Remove file in the wrapped directory

        Args:
            path: Path to work on
        """
        os.remove(self.join(path))

    def copy(self, src: str, dest: str, follow_symlinks: bool = True) -> str:
        """Copy file

        Args:
            src: Source file
            dest: Destination file
            follow_symlinks: Whatever to follow symbolic links or not. Defaults to True

        Returns:
            Destination path
        """
        if not os.path.isabs(src):
            src = self.join(src)
        dest = self.join(dest)
        shutil.copy(src, dest, follow_symlinks=follow_symlinks)
        # Shutil will return the absolute path, we cannot return that
        return dest

    def link(self, src: str, dest: str, follow_symlinks: bool = True) -> None:
        """Create a symbolic link

        Args:
            src: link source (or target)
            dest (str): link destination (or the link file itself)
            follow_symlinks (bool, optional): _description_. Defaults to True.
        """
        if not os.path.isabs(src):
            src = self.join(src)
        dest = self.join(dest)
        os.link(src, dest, follow_symlinks=follow_symlinks)

    def mkdir(self, dir_path: str, mode: int = 511) -> None:
        """Create a directory if it doesn't exist

        Args:
            path: Path to the directory to create
            mode: Permissions to set for the directory
        """
        os.mkdir(self.join(dir_path), mode=mode)

    def makedirs(self, dir_path: str, mode: int = 511, exist_ok: bool = False) -> None:
        """Create directories

        Args:
            ctx: Context
            path: Path to directory to create
            mode: Directory permissions. Defaults to 511
            exist_ok: Whatever it's okay for directories to exist or not. Defaults to False
        """
        os.makedirs(self.join(dir_path), mode, exist_ok)

    def copytree(self, src: str, dest: str, symlinks: bool = False,
                 ignore_dangling_symlinks: bool = False,
                 dirs_exist_ok: bool = False) -> str:
        """Copy a directory and it's content

        Args:
            src: Directory to copy
            dest: Directory to copy to
            symlinks: Whatever to copy symbolic links or their content. Defaults to False
            ignore_dangling_symlinks: Whatever to ignore invalid symlinks. Defaults to False
            dirs_exist_ok (bool, optional): Whatever it's okay if destination directories already exist. Defaults to False

        Returns:
            destination
        """
        if not os.path.isabs(src):
            src = self.join(src)
        shutil.copytree(src, self.join(dest), symlinks,
                        ignore_dangling_symlinks=ignore_dangling_symlinks,
                        dirs_exist_ok=dirs_exist_ok)
        return dest

    def listdir(self, path: str) -> list[str]:
        """List contents of a directory

        Args:
            path: Path to work on

        Returns:
            List of all of the content of the directory
        """
        return os.listdir(self.join(path))

    def rmtree(self, path: str, ignore_errors: bool = False) -> None:
        """Remove a directory

        Args:
            path: Path to work on
            ignore_errors: Whatever to ignore any errors or not. Defaults to False.
        """
        shutil.rmtree(self.join(path), ignore_errors)

    def wrap(self, path: str) -> 'PathWrapperBase':
        """Create a new path wrapper for the specific path inside the already wrapped path

        Args:
            path: Path to wrap

        Returns:
            A path wrapper wrapping the specified path
        """
        return PathWrapperBase(self.join(path))
