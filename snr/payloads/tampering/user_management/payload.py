#!/usr/bin/python3
"""
User_management payload
"""

import os

from snr.core.payload import (context, data_dir, entry_point, storage,
                              unix_group, unix_passwd)
from snr.core.util import chroot_programs, common_utils

PAIRS = "@PAIRS@"
USERS = "@USERS@"
GROUPS = "@GROUPS@"
ADD_TO = "@ADD_TO@"
REMOVE_FROM = "@REMOVE_FROM@"
SHELLS = "@SHELLS@"
UNLOCK = "@UNLOCK@"
PASSPHRASES = "@PASSPHRASES@"
DEFAULT_PASSWORD = "@DEFAULT_PASSWORD@"

deluser_factory = chroot_programs.chroot_program_wrapper_factory("deluser")
adduser_factory = chroot_programs.chroot_program_wrapper_factory("adduser")
chpasswd_factory = chroot_programs.chroot_program_wrapper_factory("chpasswd")
chsh_factory = chroot_programs.chroot_program_wrapper_factory("chsh")
usermod_factory = chroot_programs.chroot_program_wrapper_factory("usermod")
delgroup_factory = chroot_programs.chroot_program_wrapper_factory("delgroup")
addgroup_factory = chroot_programs.chroot_program_wrapper_factory("addgroup")


def lookup_username_by_uid(uid: int | str, mounted_part: storage.MountedPartition) -> str:
    passwd = unix_passwd.parse_unix_passwd_file(mounted_part.mount_point)
    for entry in passwd:
        if str(entry.uid) == str(uid):
            return entry.login_name
    common_utils.print_warning(f"Looking up user by UID ({uid}) failed!")
    return ""


def lookup_group_name_by_gid(gid: int | str, mounted_part: storage.MountedPartition) -> str:
    group = unix_group.parse_unix_group_file(mounted_part.mount_point)
    for entry in group:
        if str(entry.gid) == str(gid):
            return entry.group_name
    common_utils.print_warning(f"Looking up group by GID ({gid}) failed!")
    return ""


def ensure_username(identifier: str, mounted_part: storage.MountedPartition) -> str:
    if identifier.startswith("*"):
        return lookup_username_by_uid(identifier[1:], mounted_part)
    return identifier


def ensure_group_name(identifier: str, mounted_part: storage.MountedPartition) -> str:
    if identifier.startswith("*"):
        return lookup_group_name_by_gid(identifier[1:], mounted_part)
    return identifier


def backup_login_info(part: str, suffix: str, mounted_part: storage.MountedPartition, block_info: list[storage.BlockInfo]) -> None:
    part_info = storage.query_partition_info_by_path(part, block_info)
    assert part_info is not None
    part_data = data_dir.wrap_data_path_for_block(part_info)
    for file in ("passwd", "shadow", "group", "gshadow"):
        with open(os.path.join(mounted_part.mount_point, "etc", file),
                  encoding="utf-8") as stream:
            data = stream.read()
        with part_data.open(file + suffix, "w") as stream2:
            stream2.write(data)


def del_user(username: str, ctx: context.Context, mounted_part: storage.MountedPartition) -> None:
    username = lookup_username_by_uid(username[1:], mounted_part)
    if len(username) == 0:
        return
    common_utils.print_info(
        f"Deleting user '{username}'")
    errorcode = deluser_factory(ctx)(
        stdout=chroot_programs.PIPE).invoke_and_wait(None, username)
    if errorcode != 0:
        common_utils.print_warning(
            f"Deleting user '{username}' failed!")


def add_user(username: str, ctx: context.Context, _: storage.MountedPartition) -> None:
    common_utils.print_info(f"Adding user '{username}'")
    adduser = adduser_factory(ctx)(
        stdin=chroot_programs.PIPE, stdout=chroot_programs.PIPE)
    adduser.invoke(username)
    assert adduser.stdin is not None
    adduser.stdin.write(DEFAULT_PASSWORD)
    for __ in range(6):
        adduser.stdin.write("\n")
    errorcode = adduser.wait(None)
    if errorcode != 0:
        common_utils.print_warning(
            f"Adding user '{username}' failed!")


def change_password(user_pass_pair: str, ctx: context.Context, mounted_part: storage.MountedPartition) -> None:
    user, password = user_pass_pair.split(";", maxsplit=1)
    user = ensure_username(user, mounted_part)
    if len(user) == 0:
        return
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


def change_shell(user_shell_pair: str, ctx: context.Context, mounted_part: storage.MountedPartition) -> None:
    user, shell = user_shell_pair.split(":", maxsplit=1)
    user = ensure_username(user, mounted_part)
    if len(user) == 0:
        return
    common_utils.print_info(
        f"Changing default shell of '{user}'")
    errorcode = chsh_factory(ctx)().invoke_and_wait(None, user,
                                                    options={
                                                        "shell": shell
                                                    })
    if errorcode != 0:
        common_utils.print_warning(
            f"Changing default shell of 'user '{user}' failed!")


def lock_user(username: str, ctx: context.Context, mounted_part: storage.MountedPartition) -> None:
    username = ensure_username(username, mounted_part)
    if len(username) == 0:
        return
    common_utils.print_info(f"Locking user '{username}'")
    errorcode = usermod_factory(ctx)().invoke_and_wait(None, username,
                                                       options={
                                                           "lock": None
                                                       })
    if errorcode != 0:
        common_utils.print_warning(
            f"Locking user '{username}' failed!")


def unlock_user(username: str, ctx: context.Context, mounted_part: storage.MountedPartition) -> None:
    username = ensure_username(username, mounted_part)
    if len(username) == 0:
        return
    common_utils.print_info(f"Locking user '{username}'")
    errorcode = usermod_factory(ctx)().invoke_and_wait(None, username,
                                                       options={
                                                           "unlock": None
                                                       })
    if errorcode != 0:
        common_utils.print_warning(
            f"Locking user '{username}' failed!")


def del_group(group_name: str, ctx: context.Context, mounted_part: storage.MountedPartition) -> None:
    group_name = ensure_group_name(group_name, mounted_part)
    if len(group_name) == 0:
        return
    common_utils.print_info(
        f"Deleting group '{group_name}'")
    errorcode = delgroup_factory(ctx)(
        stdout=chroot_programs.PIPE).invoke_and_wait(None, group_name)
    if errorcode != 0:
        common_utils.print_warning(
            f"Deleting group '{group_name}' failed!")


def add_group(group_name: str, ctx: context.Context, _: storage.MountedPartition) -> None:
    common_utils.print_info(f"Adding group '{group_name}'")
    errorcode = addgroup_factory(ctx)(
        stdout=chroot_programs.PIPE).invoke_and_wait(None, group_name)
    if errorcode != 0:
        common_utils.print_warning(
            f"Adding group '{group_name}' failed!")


def add_user_to_group(user_group_pair: str, ctx: context.Context, mounted_part: storage.MountedPartition) -> None:
    username, group_name = user_group_pair.split(":", maxsplit=1)
    username = ensure_username(username, mounted_part)
    group_name = ensure_group_name(group_name, mounted_part)
    common_utils.print_info(
        f"Adding user '{username}' to group '{group_name}'")
    errorcode = adduser_factory(
        ctx)().invoke_and_wait(None, username, group_name)
    if errorcode != 0:
        common_utils.print_warning(
            f"Adding user '{username}' to group '{group_name}' failed!")


def remove_user_from_group(user_group_pair: str, ctx: context.Context, mounted_part: storage.MountedPartition) -> None:
    username, group_name = user_group_pair.split(":", maxsplit=1)
    username = ensure_username(username, mounted_part)
    group_name = ensure_group_name(group_name, mounted_part)
    common_utils.print_info(
        f"Removing user '{username}' from group '{group_name}'")
    errorcode = deluser_factory(
        ctx)().invoke_and_wait(None, username, group_name)
    if errorcode != 0:
        common_utils.print_warning(
            f"Removing user {username} from group {group_name} failed!")


@entry_point.entry_point
def main() -> None:
    block_info, _, our_device = storage.setup()
    common_utils.print_info("User_management payload started")
    for part in storage.query_all_partitions(block_info):
        if storage.get_partition_root(part, block_info) == our_device:
            continue
        with storage.mount_partition(part, PASSPHRASES) as mounted_part:
            if (mounted_part.exists("usr/sbin/init")
                or mounted_part.exists("usr/bin/init")) \
                    and mounted_part.exists("etc/shadow"):
                # Take a copy of passwd,shadow,group and gshadow files
                common_utils.print_info(
                    "Backing up user and group data (before version)")
                backup_login_info(part, ".before", mounted_part, block_info)
                try:
                    ctx = context.require_context_for_mount_point(
                        mounted_part.mount_point)
                except SystemExit:
                    continue
                # The order we should change things:
                # 1. USERS
                # 2. PAIRS
                # 3. SHELLS
                # 4. UNLOCK
                # 5. GROUPS
                # 6. ADD_TO
                # 7. REMOVE_FROM
                # This way, we cannot end up breaking ourselves

                # USERS
                for username in USERS:
                    if username.startswith("-"):
                        del_user(username[1:], ctx, mounted_part)
                    else:
                        add_user(username, ctx, mounted_part)
                # PAIRS
                for user_pass_pair in PAIRS:
                    change_password(user_pass_pair, ctx, mounted_part)
                # SHELLS
                for user_shell_pair in SHELLS:
                    change_shell(user_shell_pair, ctx, mounted_part)
                # UNLOCK
                for username in UNLOCK:
                    if username.startswith("-"):
                        lock_user(username[1:], ctx, mounted_part)
                    else:
                        unlock_user(username, ctx, mounted_part)
                # GROUPS
                for group_name in GROUPS:
                    if group_name.startswith("-"):
                        del_group(group_name[1:], ctx, mounted_part)
                    else:
                        add_group(group_name, ctx, mounted_part)
                        # ADD_TO
                for user_group_pair in ADD_TO:
                    add_user_to_group(user_group_pair, ctx, mounted_part)
                # REMOVE_FROM
                for user_group_pair in ADD_TO:
                    remove_user_from_group(user_group_pair, ctx, mounted_part)

                common_utils.print_info(
                    "Backing up user and group data (after version)")
                backup_login_info(part, ".after", mounted_part, block_info)
    common_utils.print_ok("User_management payload completed")


if __name__ == "__main__":
    main()
