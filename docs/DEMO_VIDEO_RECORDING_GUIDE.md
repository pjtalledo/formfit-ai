# FormFit AI — Demo Video Recording Guide (Optional Canvas Attachment)

No screen-recording tool is available in this environment, so **no `demo.mp4` was created**. This guide lets you record it yourself in 2-3 minutes if you choose to include the optional video.

## Setup
1. Start the server from `Final Project/`: `.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend`
2. Open `http://localhost:8000` in your browser.
3. Start a screen recorder (Windows: Win+Alt+R for Xbox Game Bar, or any screen-capture tool) with audio if you want to narrate.

## Script (~2-3 minutes)

1. **(0:00-0:20) Homepage and profile** — Show the FormFit AI header and the Athlete Profile panel. Briefly narrate: name, experience level, goals, equipment fields.
2. **(0:20-0:40) Save profile** — Fill in the fields, click "Save Profile," show the "Profile #N saved" confirmation.
3. **(0:40-1:10) Upload a real WOD photo** — Click "Choose from Gallery" (or "Take Photo" if recording on a phone), select a real whiteboard photo. Show the "Scanning image..." indicator.
4. **(1:10-1:30) Confirm/correct the extraction** — Show the scanned text populated in the editable textarea; make a small edit to demonstrate it's genuinely editable, not read-only.
5. **(1:30-1:50) Generate coaching** — Click "Generate Coaching Plan," show the loading state, then the resulting plan.
6. **(1:50-2:40) Review the output** — Scroll through and narrate: Warm-up, Scaling Options, Main Workout Guidance, Complementary Exercises, Safety Notes, the Usage pills (real token/cost metrics), and the Agent Trace panel (the 4 real tool-call steps).
7. **(2:40-3:00) Wrap-up** — Optionally show workout history via a browser request to `/api/athletes/{id}/history`, or simply state that results persist to SQLite.

## Explicit Rule
**Do not** narrate or imply that Video Technique Analysis is operational — it is not implemented, only tested as an isolated, undeployed experiment (see `docs/TECHNICAL_AUDIT.md` and `report.html` §7). **Do not** substitute the raw iPhone CrossFit videos in `videos/` for this screen recording — those are a separate, unrelated feasibility experiment about a different, unshipped feature, not footage of the application.

## If You Record It
Save it as `demo.mp4` in `Final Project/` (not inside `canvas_submission/` unless you've watched and listened to it end-to-end and confirmed it accurately represents the app). Only add it to the Canvas upload if you've verified it yourself — this project's standard throughout has been to never claim something works without having actually checked it.
