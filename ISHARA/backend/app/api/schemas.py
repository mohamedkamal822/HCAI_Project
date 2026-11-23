from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=300)
    exact_only: bool = False
    lang: str | None = Field(default=None, pattern="^(ar|en)$")
    simulate_error: bool = False


class FeedbackRequest(BaseModel):
    trace_id: str
    vote: str | None = Field(default=None, pattern="^(up|down)$")
    rating: str | None = Field(default=None, pattern="^(up|down)$")
    reason: str | None = Field(default=None, max_length=160)


class AlternativesRequest(BaseModel):
    trace_id: str
    lang: str | None = Field(default=None, pattern="^(ar|en)$")
