from typing import Annotated

from pydantic import Field

TaskDescriptionType = Annotated[str, Field(max_length=5000)]
TaskCommentTextType = Annotated[str, Field(max_length=2000)]
