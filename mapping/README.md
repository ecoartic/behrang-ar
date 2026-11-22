# Point-cloud map pipeline (Phase 2 — Tested Prototype, 2026-11-22)

Input: a bench capture (`.mp4` + `.json` from `bench/capture/`), walking slowly around the space.

1. Frame selection: sharpest frame in every window of 7 → ~1 frame / 0.3 s (127 frames for 36 s).
2. `sfm.py` — pycolmap 4.2.1 (CPU): SIFT (4000/img), sequential matching (overlap 12), incremental mapping, single SIMPLE_RADIAL camera.
3. Gravity: accelerometer `accelerationIncludingGravity` at each frame's timestamp, rotated into the world with the COLMAP rotation → world "up" (works on phones without a gyroscope).
4. `buildmap.py` — ORB (same parameters as the web runtime, CLAHE, 480 px long side) at each keyframe; each ORB keypoint within 2.5 px of a COLMAP observation inherits that observation's 3D point. `python buildmap.py half` = held-out evaluation.
5. `export.py` — ≤3 descriptors per 3D point, keyframe centers/view directions, desk plane, gravity, scale, coloured point-cloud preview → `map.bin` (1.5 MB).

Runtime: Behrang Lab `armap.html` (OpenCV.js): ORB → kNN match (candidate keyframes near last pose) → `solvePnPRansac` (SQPNP) → pose; between relocalizations LK optical flow + iterative PnP.
