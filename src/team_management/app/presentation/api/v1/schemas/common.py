from pydantic import BaseModel, Field


# ======================================================
# REQUEST / RESPONSE (API CONTRACT)
# ======================================================
class SuccessMessageResponse(BaseModel):
    msg: str = Field(default="Operation completed successfully")
