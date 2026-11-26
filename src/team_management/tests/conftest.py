import pytest

from app.core.config import settings


@pytest.fixture(scope="session", autouse=True)
def critical_check() -> None:
    if not settings.db.ready_for_test:
        pytest.exit(
            "Stopping tests: Database "
            f"{settings.db.DB_NAME} is not for testing."
        )
