import typing
import uuid

from sqlalchemy import UUID, Enum, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.teams.enums import TeamsRoles
from app.infrastructure.db.models.base import Base

if typing.TYPE_CHECKING:
    from app.infrastructure.db.models.meetings import Meetings
    from app.infrastructure.db.models.tasks import Tasks
    from app.infrastructure.db.models.users import Users


class Teams(Base):
    __tablename__ = "teams"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(
        String(1000), nullable=True
    )

    # ----- RELATIONSHIP -----
    membership: Mapped[list[TeamMembership]] = relationship(
        back_populates="team", init=False, default_factory=list
    )
    tasks: Mapped[list[Tasks]] = relationship(
        back_populates="team", init=False, default_factory=list
    )
    meetings: Mapped[list[Meetings]] = relationship(
        back_populates="team", init=False, default_factory=list
    )

    def __str__(self):
        return f"{self.name} ID: {self.id}"


class TeamMembership(Base, kw_only=True):
    __tablename__ = "teams_membership"

    team_role: Mapped[TeamsRoles] = mapped_column(
        Enum(TeamsRoles, native_enum=True),
        default=TeamsRoles.member,
        nullable=False,
    )

    # ------ ForeignKey ------
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
    )

    # ------ RELATIONSHIP ------
    member: Mapped[Users] = relationship(
        "Users",
        foreign_keys=[user_id],
        back_populates="membership",
        init=False,
    )
    team: Mapped[Teams] = relationship(
        "Teams",
        foreign_keys=[team_id],
        back_populates="membership",
        init=False,
    )

    __table_args__ = (
        UniqueConstraint("user_id", "team_id", name="uc_user_id_team_id"),
        Index("idx_team_user", "team_id", "user_id"),
    )
