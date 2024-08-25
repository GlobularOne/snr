"""
Change user, group and related login information. Only UNIX-like environments are supported (yet)
"""
from snr.core.payload.payload import Context, Payload, VALID_STRING


class UserManagementPayload(Payload):
    AUTHORS = ("GlobularOne",)
    TARGET_OS_LIST = ("GNU/Linux",)
    INPUTS = (
        ("PAIRS", [], -1, "User:Password pairs, Changes user's password", VALID_STRING),
        ("USERS", [], -1, "List of users to add or delete, -<USERNAME> deletes a user", VALID_STRING),
        ("GROUPS", [], -1, "List of groups to add or delete, -<USERNAME> deletes a group", VALID_STRING),
        ("ADD_TO", [], -1, "User:Group pairs, add User to Group", VALID_STRING),
        ("REMOVE_FROM", [], -1, "User:Group pairs, remove User from Group", VALID_STRING),
        ("SHELLS", [], -1, "User:Shell pairs, makes User use Shell as it's default shell", VALID_STRING),
        ("UNLOCK", [], -1, "List of users to unlock, -<USERNAME> will lock it instead", VALID_STRING),
        ("DEFAULT_PASSWORD", "Aa12!aaaaaaaaa", 32, "Default password for newly added users", VALID_STRING),
        Payload.supports_encrypted_access()
        
    )

    def generate(self, ctx: Context) -> int:
        variables = self.get_self_variables()
        self.format_payload_and_write(ctx, variables)
        self.add_autorun(ctx)
        return 0


payload = UserManagementPayload()
