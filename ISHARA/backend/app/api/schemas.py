from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=160)


class FeedbackRequest(BaseModel):
    trace_id: str
    rating: str = Field(pattern="^(up|down)$")
    reason: str | None = Field(default=None, max_length=160)
