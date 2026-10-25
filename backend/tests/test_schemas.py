import pytest
from pydantic import ValidationError

from app.schemas import ProfileCreate, ParsedWod, Recommendation


def test_profile_create_valid():
    p = ProfileCreate(
        name="Alex", experience_level="beginner", goals="get stronger",
        equipment=["barbell", "rack"], limitations="", weight_unit="lb",
    )
    assert p.name == "Alex"


def test_profile_create_rejects_bad_experience_level():
    with pytest.raises(ValidationError):
        ProfileCreate(name="Alex", experience_level="pro", goals="x", equipment=[])


def test_profile_create_rejects_empty_name():
    with pytest.raises(ValidationError):
        ProfileCreate(name="", experience_level="beginner", goals="x", equipment=[])


def test_parsed_wod_valid():
    wod = ParsedWod(
        format="For Time",
        time_cap_minutes=20,
        exercises=[{"name": "thruster", "scheme": "21-15-9"}],
    )
    assert wod.exercises[0].name == "thruster"


def test_parsed_wod_rejects_bad_format():
    with pytest.raises(ValidationError):
        ParsedWod(format="NotARealFormat", exercises=[])


def test_recommendation_requires_fields():
    with pytest.raises(ValidationError):
        Recommendation(warm_up=["jog"])  # missing required fields
