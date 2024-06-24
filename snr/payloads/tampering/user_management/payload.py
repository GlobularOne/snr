#!/usr/bin/python3
"""
"""
import os
import time

from snr.core.payload import (context, data_dir, entry_point, storage,
                              unix_group, unix_passwd)
from snr.core.util import chroot_programs, common_utils, programs

deluser_factory = chroot_programs.chroot_program_wrapper_factory("deluser")
adduser_factory = chroot_programs.chroot_program_wrapper_factory("adduser")
chpasswd_factory = chroot_programs.chroot_program_wrapper_factory("chpasswd")
chsh_factory = chroot_programs.chroot_program_wrapper_factory("chsh")
usermod_factory = chroot_programs.chroot_program_wrapper_factory("usermod")
delgroup_factory = chroot_programs.chroot_program_wrapper_factory("delgroup")
addgroup_factory = chroot_programs.chroot_program_wrapper_factory("addgroup")

PAIRS = "@PAIRS@"
USERS = "@USERS@"
GROUPS = "@GROUPS@"
ADD_TO = "@ADD_TO@"
REMOVE_FROM = "@REMOVE_FROM@"
SHELLS = "@SHELLS@"
UNLOCK = "@UNLOCK@"
PASSPHRASES = "@PASSPHRASES@"
DEFAULT_PASSWORD = "@DEFAULT_PASSWORD@"

FS_MOUNTPOINT = "/mnt"


def lookup_username_by_uid(uid: int | str) -> str:
    passwd = unix_passwd.parse_unix_passwd_file(FS_MOUNTPOINT)
    for entry in passwd:
        if str(entry.uid) == str(uid):
            return entry.login_name
    common_utils.print_warning(f"Looking up user by UID ({uid}) failed!")
    return ""


def lookup_group_name_by_gid(gid: int | str) -> str:
    group = unix_group.parse_unix_group_file(FS_MOUNTPOINT)
    for entry in group:
        if str(entry.gid) == str(gid):
            return entry.group_name
    common_utils.print_warning(f"Looking up group by GID ({gid}) failed!")
    return ""


def backup_login_info(part: str, suffix: str = ".before") -> None:
    for file in ("passwd", "shadow", "group", "gshadow"):
        with open(f"/{FS_MOUNTPOINT}/etc/{file}",
                  encoding="utf-8") as stream:
            data = stream.read()
        with data_dir.data_open(os.path.join(part.replace("/", ".")[1:], file + suffix), "w") as stream2:
            stream2.write(data)


@entry_point.entry_point
def main() -> None:
    storage.lvm_scan_all()
    storage.lvm_activate_all_vgs()
    block_info = storage.query_all_block_info()
    common_utils.print_ok("User_management payload started")
    root_ctx = context.create_context_for_mount_point("/")
    if root_ctx is None:
        common_utils.print_error("Creating context for / failed")
        return None
    our_device = storage.get_partition_root(root_ctx.device_name, block_info)
    if our_device is None:
        common_utils.print_error("Finding partition root device for / failed")
        return None
    for part in storage.query_all_partitions(block_info):
        if storage.get_partition_root(part, block_info) == our_device:
            continue
        luks_encrypted = storage.luks_is_partition_encrypted(part)
        luks_name = part.split(os.path.sep)[-1] + "_crypt"
        if luks_encrypted:
            common_utils.print_info(
                "Luks encrypted partition found! Trying available passphrases...")
            for passphrase in PASSPHRASES:
                if storage.luks_open(part, luks_name, passphrase):
                    common_utils.print_info("Luks partition opened!")
                    break
            else:
                try:
                    common_utils.print_warning(
                        "Passphrase not found! Press Ctrl + C to try a passphrase")
                    time.sleep(5)
                except KeyboardInterrupt:
                    try:
                        while True:
                            common_utils.print_info(
                                "Enter new passphrase or press Ctrl + C again to abort: ", end="")
                            passphrase = input()
                            if storage.luks_open(part, luks_name, passphrase):
                                common_utils.print_info(
                                    "Luks partition opened!")
                                break
                    except KeyboardInterrupt:
                        common_utils.print_warning(
                            f"No passphrase found for partition '{part}', ignoring partition.")
                        continue
            part = f"/dev/mapper/{luks_name}"
        # Try to mount it and see if it sounds like something like unix
        errorcode = programs.Mount().invoke_and_wait(None, part, FS_MOUNTPOINT)
        if errorcode != 0:
            common_utils.print_error(
                f"Failed to mount partition '{part}'! Skipping partition")
            if luks_encrypted:
                storage.luks_close(luks_name)
            continue
        if os.path.exists(f"/{FS_MOUNTPOINT}/usr/sbin/init") or os.path.exists(f"/{FS_MOUNTPOINT}/usr/bin/init"):
            data_dir.data_mkdir(part.replace("/", ".")[1:])
            # Take a copy of passwd,shadow,group and gshadow files
            common_utils.print_info(
                "Backing up user and group data (before version)")
            backup_login_info(part)
            # The order we should change things:
            # 1. USERS
            # 2. PAIRS
            # 3. SHELLS
            # 4. UNLOCK
            # 5. GROUPS
            # 6. ADD_TO
            # 7. REMOVE_FROM
            # This way, we cannot end up breaking ourselves
            ctx = context.create_context_for_mount_point(FS_MOUNTPOINT)
            if ctx is None:
                common_utils.print_warning(
                    "Creating context for partition failed! Ignoring filesystem")
                if luks_encrypted:
                    storage.luks_close(luks_name)
                continue
            # USERS
            for username in USERS:
                if username.startswith("-"):
                    username = username[1:]
                    if username.startswith("*"):
                        # Referenced by UID, not username. Find the username and continue
                        username = lookup_username_by_uid(username[1:])
                        if len(username) == 0:
                            continue
                        common_utils.print_info(f"Deleting user '{username}'")
                        errorcode = deluser_factory(ctx)(
                            stdout=chroot_programs.PIPE).invoke_and_wait(None, username)
                        if errorcode != 0:
                            common_utils.print_warning(
                                f"Deleting user '{username}' failed!")
                else:
                    common_utils.print_info(f"Adding user '{username}'")
                    adduser = adduser_factory(ctx)(
                        stdin=chroot_programs.PIPE, stdout=chroot_programs.PIPE)
                    adduser.invoke(username)
                    assert adduser.stdin is not None
                    adduser.stdin.write(DEFAULT_PASSWORD)
                    for _ in range(6):
                        adduser.stdin.write("\n")
                    errorcode = adduser.wait(None)
                    if errorcode != 0:
                        common_utils.print_warning(
                            f"Adding user '{username}' failed!")
            # PAIRS
            for user_data in PAIRS:
                user, password = user_data.split(";", maxsplit=1)
                if user.startswith("*"):
                    user = lookup_username_by_uid(user[1:])
                    if len(user) == 0:
                        continue
                common_utils.print_info(f"Changing password of '{user}'")
                chpasswd = chpasswd_factory(ctx)(
                    stdin=chroot_programs.PIPE)
                chpasswd.invoke()
                assert chpasswd.stdin is not None
                chpasswd.stdin.write(f"{user}:{password}\n")
                chpasswd.stdin.close()
                errorcode = chpasswd.wait(None)
                if errorcode != 0:
                    common_utils.print_warning(
                        f"Changing password for '{user}' failed!")
            # SHELLS
            for user_shell in SHELLS:
                user, shell = user_shell.split(":", maxsplit=1)
                if user.startswith("*"):
                    user = lookup_username_by_uid(user[1:])
                    if len(user) == 0:
                        continue
                    common_utils.print_info(
                        f"Changing default shell of '{user}'")
                    errorcode = chsh_factory(ctx)().invoke_and_wait(None, user,
                                                                    options={
                                                                        "shell": shell
                                                                    })
                    if errorcode != 0:
                        common_utils.print_warning(
                            f"Changing default shell of 'user '{user}' failed!")
            # UNLOCK
            for user in UNLOCK:
                if user.startswith("-"):
                    if user.startswith("*"):
                        user = lookup_username_by_uid(user[1:])
                        if len(user) == 0:
                            continue
                    common_utils.print_info(f"Locking user '{user}'")
                    errorcode = usermod_factory(ctx)().invoke_and_wait(None, user,
                                                                       options={
                                                                           "lock": None
                                                                       })
                    if errorcode != 0:
                        common_utils.print_warning(
                            f"Locking user '{user}' failed!")
                else:
                    if user.startswith("*"):
                        user = lookup_username_by_uid(user[1:])
                        if len(user) == 0:
                            continue
                    common_utils.print_info(f"Unlocking user '{user}'")
                    errorcode = usermod_factory(ctx)().invoke_and_wait(None, user,
                                                                       options={
                                                                           "unlock": None
                                                                       })
                    if errorcode != 0:
                        common_utils.print_warning(
                            f"Unlocking user '{user}' failed!")
            # GROUPS
            for group_name in GROUPS:
                if group_name.startswith("-"):
                    group_name = group_name[1:]
                    if group_name.startswith("*"):
                        # Referenced by GID, not group name. Find the group name and continue
                        group_name = lookup_group_name_by_gid(group_name[1:])
                        if len(group_name) == 0:
                            continue
                        common_utils.print_info(
                            f"Deleting group '{group_name}'")
                        errorcode = delgroup_factory(ctx)(
                            stdout=chroot_programs.PIPE).invoke_and_wait(None, group_name)
                        if errorcode != 0:
                            common_utils.print_warning(
                                f"Deleting group '{group_name}' failed!")
                else:
                    common_utils.print_info(f"Adding group '{group_name}'")
                    errorcode = addgroup_factory(ctx)(
                        stdout=chroot_programs.PIPE).invoke_and_wait(None, group_name)
                    if errorcode != 0:
                        common_utils.print_warning(
                            f"Adding group '{group_name}' failed!")
            # ADD_TO
            for user_data in ADD_TO:
                user, group = user_data.split(":", maxsplit=1)
                if user.startswith("*"):
                    user = lookup_username_by_uid(user[1:])
                    if len(user) == 0:
                        continue
                if group.startswith("*"):
                    group = lookup_group_name_by_gid(group[1:])
                    if len(group) == 0:
                        continue
                common_utils.print_info(
                    f"Adding user '{user}' to group '{group}'")
                errorcode = adduser_factory(
                    ctx)().invoke_and_wait(None, user, group)
                if errorcode != 0:
                    common_utils.print_warning(
                        f"Adding user '{user}' to group '{group}' failed!")
            # REMOVE_FROM
            for user_data in ADD_TO:
                user, group = user_data.split(":", maxsplit=1)
                if user.startswith("*"):
                    user = lookup_username_by_uid(user[1:])
                    if len(user) == 0:
                        continue
                if group.startswith("*"):
                    group = lookup_group_name_by_gid(group[1:])
                    if len(group) == 0:
                        continue
                common_utils.print_info(
                    f"Removing user '{user}' from group '{group}'")
                errorcode = deluser_factory(
                    ctx)().invoke_and_wait(None, user, group)
                if errorcode != 0:
                    common_utils.print_warning(
                        f"Removing user {user} from group {group} failed!")
            common_utils.print_info(
                "Backing up user and group data (after version)")
            backup_login_info(part, suffix=".after")
            common_utils.print_ok("")
        programs.Umount().invoke_and_wait(None, FS_MOUNTPOINT)
        if luks_encrypted:
            storage.luks_close(luks_name)
    common_utils.print_ok("User_management payload completed")


if __name__ == "__main__":
    main()
