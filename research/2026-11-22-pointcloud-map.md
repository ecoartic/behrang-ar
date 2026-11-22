# 2026-11-22 — Markerless AR on a point-cloud map (first real test)

Data: Samsung M13, desk with many objects against a wall, 36 s walk (arc in front of the desk), 720×1280, 23.6 fps real.

## Mapping (CPU, pycolmap 4.2.1)
- 127 frames → **127/127 registered**, 20,575 points, mean track length 9.6, **reprojection error 0.78 px**. Extract 62 s, match 29 s, map 100 s.
- Intrinsics: f = 502.7 px @ 720×1280 (HFOV ≈ 71°), k1 = −0.012.
- Gravity from accelerometer vs COLMAP rotations: mean cosine **0.99977** across 127 frames (≈ 1° agreement) → strong check of both.
- Height histogram along gravity: floor peak −9.74, desk-top −3.55 units → scale 0.121 m/unit **assuming a 75 cm desk** (to be confirmed by a measurement).

## Localization accuracy (held-out, Python, same ORB params as web)
Map from even frames, localize odd frames: **63/63 localized**, position error median 0.022 units (**≈ 2.7 mm**), p90 0.048 (≈ 5.8 mm), rotation median **0.11°**, PnP inliers median 639.
Caveat: held-out frames are temporal neighbours of map frames → optimistic.

## Web runtime (headless Chrome, fake camera = same video at 360×640)
- Localized **58 of 60** half-second samples over 30 s; 377–569 PnP inliers; 15–32 ms per frame (swiftshader desktop).
- Point-cloud overlay lands on the right objects (bottles, red jar, orange folder) → pose + intrinsics consistent.
- Model placed on the desk plane stays at the same physical spot from all viewpoints.

## Known limits / next
1. Same phone + same space only (intrinsics from the map; other phones need FOV estimate or self-calibration).
2. Scale assumption (75 cm desk) → replace with a measured reference (A4 detection or user input).
3. Mapping is offline in Python → next: in-browser mapping (OpenCV.js SfM-lite) or upload-and-build on the PC (RTX 4080) with MapAnything/VGGT for denser, metric maps.
4. Test on the phone live (lighting changes, people moving).
