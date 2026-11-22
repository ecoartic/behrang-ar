# Roadmap

| Phase | Status | Exit criterion |
|---|---|---|
| 0 Bench capture + eval | In Progress (2026-11-22) | ≥ 3 phones × 5 surfaces recorded, timing/IMU report per phone |
| 1 AI surface tracker (web) | Proposed | beats MindAR: ≥2× detection on low-texture, <2 px jitter, ≥20 fps budget Android |
| 2 Depth: occlusion + shadows | Proposed | model occluded correctly by a hand in ≥80% of test frames |
| 3 Markerless VIO (Android) | Proposed / research | 1 m walk with <3% drift on a non-ARCore phone |

## Phase 1 work items
1. Export XFeat (sparse, 64-D) and LighterGlue to ONNX; verify ops on ORT-Web WebGPU; fp16 variant.
2. Target build: keypoints/descriptors at 3 scales of the captured surface (replaces `.mind`).
3. Runtime: detect every N frames or on loss; Lucas–Kanade flow between frames; RANSAC homography; pose from homography + estimated focal length.
4. Filter: One-Euro on pose; optional gyro prediction between detections.
5. Swap into Behrang Lab `artarget.html` behind a toggle (MindAR vs Behrang AR) → A/B on the same phone.
