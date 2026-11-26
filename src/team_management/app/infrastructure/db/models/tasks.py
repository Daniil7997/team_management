import typing
import uuid
from datetime import date

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.tasks.enums import TaskStatus
from app.infrastructure.db.models.base import Base

if typing.TYPE_CHECKING:
    from app.infrastructure.db.models.evaluations import Evaluations
    from app.infrastructure.db.models.teams import Teams
    from app.infrastructure.db.models.users import Users


class Tasks(Base, kw_only=True):
    __tablename__ = "tasks"

    description: Mapped[str] = mapped_column(String(2000))
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, native_enum=True),
        default=TaskStatus.open,
        nullable=False,
    )
    due_date: Mapped[date] = mapped_column(nullable=False, index=True)
    verification_url: Mapped[str | None] = mapped_column(
        String(500), default=None, init=False
    )
    # ------ ForeignKey ------
    creator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
    )
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        default=None,
        index=True,
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        index=True,
    )

    # ------ RELATIONSHIP ------
    # Users
    creator: Mapped[Users] = relationship(
        back_populates="created_tasks", foreign_keys=[creator_id], init=False
    )
    assignee: Mapped[Users | None] = relationship(
        back_populates="assigned_tasks", foreign_keys=[assignee_id], init=False
    )
    # Teams
    team: Mapped[Teams] = relationship(
        foreign_keys=[team_id], back_populates="tasks", init=False
    )
    # Evaluations
    evaluations: Mapped[Evaluations] = relationship(
        back_populates="tasks", init=False
    )
