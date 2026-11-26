from enum import StrEnum


class TeamsRoles(StrEnum):
    manager = "manager"
    member = "member"

    @property
    def access_level(self) -> int:
        """Assigns a numeric access level to each string role."""
        levels = {TeamsRoles.manager: 2, TeamsRoles.member: 1}
        return levels[self]

    def __ge__(self, other) -> bool:
        if not isinstance(other, TeamsRoles):
            return NotImplemented
        return self.access_level >= other.access_level

    def __gt__(self, other) -> bool:
        if not isinstance(other, TeamsRoles):
            return NotImplemented
        return self.access_level > other.access_level

    def __le__(self, other) -> bool:
        if not isinstance(other, TeamsRoles):
            return NotImplemented
        return self.access_level <= other.access_level

    def __lt__(self, other) -> bool:
        if not isinstance(other, TeamsRoles):
            return NotImplemented
        return self.access_level < other.access_level

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value
