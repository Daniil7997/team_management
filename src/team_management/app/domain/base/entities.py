import datetime as dt

from pydantic import BaseModel, ConfigDict


class BaseDomainEntity(BaseModel):
    """Base class for ALL entities"""

    created_at: dt.datetime
    updated_at: dt.datetime

    model_config = ConfigDict(frozen=True, from_attributes=True)
