"""
Snr version info
"""
import shutil as _shutil
import subprocess as _subprocess

__all__ = (
    "MAJOR", "MINOR",
    "PATCH", "__version__"
)

_LOCAL_VERSION = ""
_git_path = _shutil.which("git")
if _git_path is not None:
    try:
        _git_commit = _subprocess.check_output(
            [_git_path, "rev-parse", "--short", "HEAD"], text=True, stderr=_subprocess.DEVNULL).strip("\n")
        _git_changes = _subprocess.check_output(
            [_git_path, "status", "-s"], text=True, stderr=_subprocess.DEVNULL).strip("\n")
        if len(_git_changes.strip()) != 0:
            _git_commit += "*"
        _LOCAL_VERSION += "+git" + _git_commit
    except _subprocess.CalledProcessError:
        pass

MAJOR = "1"
MINOR = "2"
PATCH = "0" + _LOCAL_VERSION
HOMEPAGE = "https://github.com/GlobularOne/snr"

__version__ = ".".join([MAJOR, MINOR, PATCH])
