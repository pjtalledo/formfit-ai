"""
Curated exercise knowledge base. Generation/guidance features are constrained
to this list to prevent hallucinated or unsafe movements (see
docs/ARCHITECTURE.md and docs/FEASIBILITY_MATRIX.md).
"""

EXERCISES = {
    "air squat": {"category": "gymnastics", "scaling": ["box squat", "reduce reps"], "equipment": []},
    "push-up": {"category": "gymnastics", "scaling": ["knee push-up", "incline push-up"], "equipment": []},
    "pull-up": {"category": "gymnastics", "scaling": ["ring row", "banded pull-up", "jumping pull-up"], "equipment": ["pull-up bar"]},
    "burpee": {"category": "conditioning", "scaling": ["step-back burpee", "no push-up burpee"], "equipment": []},
    "box jump": {"category": "gymnastics", "scaling": ["step-up", "lower box"], "equipment": ["box"]},
    "wall ball": {"category": "conditioning", "scaling": ["lighter ball", "lower target"], "equipment": ["medicine ball"]},
    "deadlift": {"category": "strength", "scaling": ["reduce load", "kettlebell deadlift"], "equipment": ["barbell", "plates"]},
    "back squat": {"category": "strength", "scaling": ["front squat", "goblet squat", "reduce load"], "equipment": ["barbell", "rack"]},
    "front squat": {"category": "strength", "scaling": ["goblet squat", "reduce load"], "equipment": ["barbell", "rack"]},
    "clean": {"category": "olympic weightlifting", "scaling": ["hang clean", "dumbbell clean", "reduce load"], "equipment": ["barbell", "plates"]},
    "snatch": {"category": "olympic weightlifting", "scaling": ["hang snatch", "dumbbell snatch", "reduce load"], "equipment": ["barbell", "plates"]},
    "thruster": {"category": "olympic weightlifting", "scaling": ["dumbbell thruster", "reduce load"], "equipment": ["barbell", "plates"]},
    "kettlebell swing": {"category": "conditioning", "scaling": ["lighter kettlebell", "dumbbell swing"], "equipment": ["kettlebell"]},
    "double-under": {"category": "gymnastics", "scaling": ["single-under", "reduce reps"], "equipment": ["jump rope"]},
    "row (erg)": {"category": "conditioning", "scaling": ["reduce calories/meters"], "equipment": ["rower"]},
    "run": {"category": "conditioning", "scaling": ["reduce distance", "bike substitute"], "equipment": []},
    "toes-to-bar": {"category": "gymnastics", "scaling": ["knee raise", "hanging leg raise"], "equipment": ["pull-up bar"]},
    "handstand push-up": {"category": "gymnastics", "scaling": ["pike push-up", "box-assisted hspu"], "equipment": []},
    "overhead squat": {"category": "olympic weightlifting", "scaling": ["PVC pipe", "reduce load"], "equipment": ["barbell", "plates"]},
    "muscle-up": {"category": "gymnastics", "scaling": ["pull-up + dip combo", "banded muscle-up"], "equipment": ["pull-up bar", "rings"]},
}

CORRECTIVE_DRILLS = {
    "shoulder mobility": ["band pass-throughs", "PVC pipe shoulder dislocates", "wall slides"],
    "hip mobility": ["90/90 hip stretch", "couch stretch", "goblet squat hold"],
    "ankle mobility": ["banded ankle distraction", "wall ankle stretch"],
    "core stability": ["dead bug", "plank hold", "hollow body hold"],
    "posterior chain weakness": ["glute bridge", "Romanian deadlift (light)", "banded good morning"],
}


def is_known_exercise(name: str) -> bool:
    """
    Matches case-insensitively and tolerates simple plural forms (e.g. the
    model naturally writes "Thrusters"/"Pull-ups" for KB keys "thruster"/
    "pull-up"). Found as a real bug via a live screenshot in Phase 3 — the
    exact-match version flagged nearly every common plural exercise name as
    "unknown to KB" even though it was present, undermining the WOD
    Generator's accuracy claims (see docs/TECHNICAL_AUDIT.md Phase 3 entry).
    """
    normalized = name.strip().lower()
    if normalized in EXERCISES:
        return True
    if normalized.endswith("s") and normalized[:-1] in EXERCISES:
        return True
    return False


def known_exercise_names() -> list[str]:
    return list(EXERCISES.keys())
