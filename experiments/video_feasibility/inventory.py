"""
Isolated feasibility experiment — NOT part of the production app.
Inventories video files: format, duration, resolution, fps, file size.
No model calls here.
"""
import os
import cv2

VIDEO_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "videos")

for fname in sorted(os.listdir(VIDEO_DIR)):
    path = os.path.join(VIDEO_DIR, fname)
    size_mb = os.path.getsize(path) / (1024 * 1024)
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        print(f"{fname}: COULD NOT OPEN ({size_mb:.1f} MB)")
        continue
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration_s = frame_count / fps if fps else 0
    cap.release()
    print(f"{fname}: {size_mb:.1f}MB, {width}x{height}, {fps:.1f}fps, {duration_s:.1f}s, ~{int(frame_count)} frames")
