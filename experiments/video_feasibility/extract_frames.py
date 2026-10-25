"""
Isolated feasibility experiment — extracts representative frames from each
video for human (Claude) visual inspection, WITHOUT any model API calls.
"""
import os
import cv2

VIDEO_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "videos")
OUT_DIR = os.path.join(os.path.dirname(__file__), "frames")
os.makedirs(OUT_DIR, exist_ok=True)

# Shortest videos first — cheapest to review, likely single-movement clips
targets = ["IMG_3085.MOV", "IMG_E3086.MOV", "IMG_3087.MOV", "IMG_2363.MOV"]

for fname in targets:
    path = os.path.join(VIDEO_DIR, fname)
    cap = cv2.VideoCapture(path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # 4 evenly spaced frames per video
    positions = [int(frame_count * p) for p in (0.1, 0.4, 0.6, 0.9)]
    base = os.path.splitext(fname)[0]
    for i, pos in enumerate(positions):
        cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
        ok, frame = cap.read()
        if ok:
            out_path = os.path.join(OUT_DIR, f"{base}_frame{i}.jpg")
            cv2.imwrite(out_path, frame)
            print(f"saved {out_path}")
    cap.release()
