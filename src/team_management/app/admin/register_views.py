from starlette_admin.contrib.sqla import Admin

from app.admin.tasks import TasksView
from app.admin.teams import TeamMembershipView, TeamsView
from app.admin.users import UsersView
from app.infrastructure.db.models.tasks import Tasks
from app.infrastructure.db.models.teams import TeamMembership, Teams
from app.infrastructure.db.models.users import Users


def register_admin_views(admin: Admin):
    admin.add_view(
        UsersView(Users, menu_label="Users", display_name="User", key="users")
    )
    admin.add_view(
        TeamsView(Teams, menu_label="Teams", display_name="Team", key="teams")
    )
    admin.add_view(
        TeamMembershipView(
            TeamMembership,
            menu_label="Teams Memberships",
            display_name="Members",
            key="team_membership",
        )
    )
    admin.add_view(
        TasksView(Tasks, menu_label="Tasks", display_name="Task", key="tasks")
    )
