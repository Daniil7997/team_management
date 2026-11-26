from typing import Any

from starlette.requests import Request
from starlette_admin.contrib.sqla import ModelView


class BaseSQLAView(ModelView):
    async def create(self, request: Request, data: dict[str, Any]) -> Any:
        session = request.state.session
        obj = self.model(**data)
        session.add(obj)
        session.flush()
        return obj

    async def edit(
        self, request: Request, pk: Any, data: dict[str, Any]
    ) -> Any:
        session = request.state.session
        obj = self.find_by_pk(request, pk)
        for key, value in data.items():
            setattr(obj, key, value)
        session.add(obj)
        session.flush()
        return obj

    async def repr(self, obj: Any, request: Request) -> str:
        return str(obj)
