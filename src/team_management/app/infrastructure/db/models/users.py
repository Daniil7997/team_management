import typing

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.models.base import Base

if typing.TYPE_CHECKING:
    from app.infrastructure.db.models.evaluations import Evaluations
    from app.infrastructure.db.models.meetings import Meetings
    from app.infrastructure.db.models.tasks import Tasks
    from app.infrastructure.db.models.teams import TeamMembership


class Users(Base):
    __tablename__ = "users"
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(
        default=False, nullable=False, init=True
    )
    is_active: Mapped[bool] = mapped_column(
        default=True, nullable=False, init=False
    )

    # ------ RELATIONSHIP ------
    # Teams
    membership: Mapped[list[TeamMembership]] = relationship(
        "TeamMembership",
        back_populates="member",
        init=False,
        default_factory=list,
    )
    # Meetings
    meetings: Mapped[list[Meetings]] = relationship(
        secondary="meetings_participants",
        back_populates="users",
        init=False,
        default_factory=list,
    )
    # Tasks
    created_tasks: Mapped[list[Tasks]] = relationship(
        foreign_keys="[Tasks.creator_id]",
        back_populates="creator",
        init=False,
        default_factory=list,
    )
    assigned_tasks: Mapped[list[Tasks]] = relationship(
        foreign_keys="[Tasks.assignee_id]",
        back_populates="assignee",
        init=False,
        default_factory=list,
    )
    # Evaluations
    grades_given: Mapped[list[Evaluations]] = relationship(
        back_populates="grader",
        init=False,
        default_factory=list,
        foreign_keys="[Evaluations.grader_id]",
    )
    grades_recieved: Mapped[list[Evaluations]] = relationship(
        back_populates="author",
        init=False,
        default_factory=list,
        foreign_keys="[Evaluations.author_id]",
    )

    def __str__(self):
        return f"{self.name} {self.email} ID: {self.id}"
