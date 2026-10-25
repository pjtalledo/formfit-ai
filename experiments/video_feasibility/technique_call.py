"""
Isolated feasibility experiment — NOT part of the production app. Does not
import or modify backend/app/agent.py or portkey_client.py. Sends several
extracted frames from one video as a multi-image message to the
course-approved model, asking for observable-only technique notes.
"""
import base64
import sys
import os
import glob

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
from app.config import PORTKEY_API_KEY, PORTKEY_BASE_URL, APPROVED_MODEL  # noqa: E402
from openai import OpenAI  # noqa: E402

SYSTEM_PROMPT = (
    "You are assisting with a CrossFit/weightlifting technique feasibility review. "
    "You are shown several still frames extracted from one short video, in rough "
    "time order. These are NOT a continuous video and you cannot infer motion "
    "blur, tempo, or timing between frames beyond what each frame shows.\n\n"
    "Rules:\n"
    "1. Only describe body positions and bar/equipment positions you can actually "
    "see in these specific frames. Do not infer anything about frames you were not "
    "shown.\n"
    "2. Identify the likely movement/exercise and phase (e.g., 'catch position of a "
    "clean', 'overhead lockout') but explicitly flag this as an inference with a "
    "confidence level, not a certainty.\n"
    "3. You may note observable position/alignment details (e.g., knee position "
    "relative to toes, torso angle, bar path relative to body) ONLY as neutral "
    "observations, never as a confirmed technique fault.\n"
    "4. You MUST NOT make any medical, injury-risk, or biomechanical-accuracy claims. "
    "Do not say an angle is 'unsafe', 'incorrect', or 'likely to cause injury'. You may "
    "at most say a position 'may be worth a human coach's attention' with an explicit "
    "uncertainty caveat.\n"
    "5. If frames are ambiguous, blurry, or you cannot confidently identify something, "
    "say so explicitly rather than guessing."
)


def analyze(video_label: str, frame_paths: list[str]):
    client = OpenAI(api_key=PORTKEY_API_KEY, base_url=PORTKEY_BASE_URL, timeout=60.0)
    content = [{"type": "text", "text": f"These {len(frame_paths)} frames are from one video clip ({video_label}), in time order. What do you observe?"}]
    for p in frame_paths:
        with open(p, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}})

    response = client.chat.completions.create(
        model=APPROVED_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": content},
        ],
        timeout=60.0,
    )
    print(f"=== {video_label} ===")
    print(response.choices[0].message.content)
    print("USAGE:", response.usage)
    print()


if __name__ == "__main__":
    frames_dir = os.path.join(os.path.dirname(__file__), "frames")

    call1_frames = sorted(glob.glob(os.path.join(frames_dir, "IMG_E3086_frame*.jpg")))
    analyze("IMG_E3086.MOV (catch/squat clip)", call1_frames)

    call2_frames = sorted(glob.glob(os.path.join(frames_dir, "IMG_3085_frame*.jpg")))
    analyze("IMG_3085.MOV (overhead clip)", call2_frames)
