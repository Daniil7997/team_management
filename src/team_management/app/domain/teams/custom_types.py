from typing import Annotated

from pydantic import Field

TeamNameType = Annotated[str, Field(max_length=100)]
TeamDescriptionType = Annotated[str | None, Field(max_length=1000)]
