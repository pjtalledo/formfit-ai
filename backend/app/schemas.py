from typing import Literal
from pydantic import BaseModel, Field, field_validator


class ProfileCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    experience_level: Literal["beginner", "intermediate", "advanced"]
    goals: str = Field(min_length=1, max_length=500)
    equipment: list[str] = Field(default_factory=list)
    limitations: str = Field(default="", max_length=500)
    weight_unit: Literal["lb", "kg"] = "lb"

    @field_validator("equipment")
    @classmethod
    def equipment_not_too_long(cls, v: list[str]) -> list[str]:
        if len(v) > 30:
            raise ValueError("equipment list too long")
        return v


class ProfileOut(ProfileCreate):
    id: int


class WodExercise(BaseModel):
    name: str
    scheme: str  # e.g. "5 rounds", "21-15-9", "AMRAP 12"
    reps: str | None = None
    load_note: str | None = None


class ParsedWod(BaseModel):
    format: Literal["AMRAP", "EMOM", "For Time", "Strength", "Other"]
    time_cap_minutes: int | None = None
    exercises: list[WodExercise]
    notes: str | None = None


class Recommendation(BaseModel):
    warm_up: list[str]
    scaling_options: list[str]
    main_workout_guidance: str
    complementary_exercises: list[str]
    safety_notes: list[str] = Field(default_factory=list)


class WodRequest(BaseModel):
    athlete_id: int
    raw_text: str = Field(min_length=3, max_length=4000)
    source: Literal["typed", "image"] = "typed"


class UsageMetadata(BaseModel):
    model: str
    prompt_tokens: int
    completion_tokens: int
    cached_tokens: int = 0
    estimated_cost_usd: float


class WodScanResult(BaseModel):
    extracted_text: str
    low_confidence: bool
    confidence_notes: list[str] = Field(default_factory=list)
    usage: UsageMetadata


class WodResponse(BaseModel):
    id: int
    parsed_wod: ParsedWod
    recommendation: Recommendation
    usage: UsageMetadata
    agent_trace: list[dict]
