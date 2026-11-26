import uuid


def generate_invite_code() -> uuid.UUID:
    return uuid.uuid7()
