from app.database import AthleteProfile, WorkoutResult


def test_profile_persists(test_db):
    record = AthleteProfile(
        name="Jordan", experience_level="intermediate", goals="conditioning",
        equipment=["kettlebell"], limitations="knee", weight_unit="kg",
    )
    test_db.add(record)
    test_db.commit()
    test_db.refresh(record)

    assert record.id is not None
    fetched = test_db.get(AthleteProfile, record.id)
    assert fetched.name == "Jordan"
    assert fetched.equipment == ["kettlebell"]


def test_workout_result_persists_with_trace(test_db):
    profile = AthleteProfile(name="Sam", experience_level="beginner", goals="x", equipment=[])
    test_db.add(profile)
    test_db.commit()
    test_db.refresh(profile)

    result = WorkoutResult(
        athlete_id=profile.id,
        source="typed",
        raw_input="21-15-9 thrusters pull-ups",
        parsed_wod={"format": "For Time", "exercises": []},
        recommendation={"warm_up": [], "scaling_options": [], "main_workout_guidance": "x", "complementary_exercises": []},
        model_used="gpt-6-luna",
        prompt_tokens=100,
        completion_tokens=50,
        cached_tokens=0,
        estimated_cost_usd=0.0,
        agent_trace=[{"tool": "parse_wod_tool", "ok": True}],
    )
    test_db.add(result)
    test_db.commit()
    test_db.refresh(result)

    fetched = test_db.get(WorkoutResult, result.id)
    assert fetched.model_used == "gpt-6-luna"
    assert fetched.agent_trace[0]["tool"] == "parse_wod_tool"


def test_data_survives_session_reopen(test_db, tmp_path):
    profile = AthleteProfile(name="Persisted", experience_level="advanced", goals="x", equipment=[])
    test_db.add(profile)
    test_db.commit()
    profile_id = profile.id

    from app import database as db_module
    new_session = db_module.SessionLocal()
    try:
        fetched = new_session.get(AthleteProfile, profile_id)
        assert fetched is not None
        assert fetched.name == "Persisted"
    finally:
        new_session.close()
