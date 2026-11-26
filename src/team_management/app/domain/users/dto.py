import datetime as dt

from pydantic import BaseModel, ConfigDict

from app.domain.shared.custom_types import IdType


class BaseSchema(BaseModel):
    id: IdType
    created_at: dt.datetime
    updated_at: dt.datetime

    model_config = ConfigDict(from_attributes=True)
