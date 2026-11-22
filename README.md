# Behrang AR

**AI-assisted AR that works beyond the ARCore / ARKit device lists.**
Goal: robust surface tracking on any phone camera — including cheap Android devices without ARCore — first in the browser, later markerless.

> Status (2026-11-22): **Phase 0 — In Progress.** Baseline exists: [artarget on Behrang Lab](https://ecoartic.github.io/opuscar-studio/artarget.html) (MindAR, user-captured surfaces, on-camera gizmo).

## Why
- ARKit works on every iPhone because Apple calibrates every camera/IMU pair at the factory. Android has hundreds of models; ARCore is software-locked to certified ones, and the browser (WebXR) inherits that lock.
- Without ARCore, the web only offers image-target tracking with hand-crafted features (MindAR, AR.js). These fail on low-texture surfaces, weak cameras and bad light.
- Learned local features (XFeat, LightGlue) are now fast enough to run in the browser via WebGPU. Nobody ships them as a general-purpose web AR tracker yet.

## Architecture

| Phase | Deliverable | Stack | Runs on |
|---|---|---|---|
| **0. Bench** | Capture video + IMU + frame timestamps from many phones; metrics: jitter (px RMS), time-to-detect, lost-track %, drift | Web capture page + Python eval | Phones → PC (RTX 4080 SUPER) |
| **1. AI surface tracker** | Replace MindAR's hand-crafted features: learned keypoints for detection, optical flow between frames, homography → pose, One-Euro filter, gyro fusion | XFeat + LighterGlue → ONNX Runtime Web (WebGPU, WASM fallback) | Any phone browser |
| **2. Scene understanding** | Monocular depth for occlusion, contact shadows and table-plane detection (not tracking) | Depth Anything V2 Small | Browser / WebGPU |
| **3. Markerless** | VIO with online camera/IMU/time-offset calibration for non-ARCore phones | OpenVINS-class VIO (license TBD) | Native Android |

```
camera frame ──► detect (XFeat, every N frames / on loss) ──► match to target (LighterGlue)
       │                                                        │
       └──► track (optical flow, every frame) ◄── homography ◄──┘
                       │
        gyro (DeviceMotion) ──► fusion + One-Euro ──► pose ──► three.js
```

## Acceptance criteria — Phase 1
Measured on 3 phones (iPhone, ARCore Android, budget non-ARCore Android) × 5 surfaces (card, book, wooden table, rug, newspaper), against the MindAR baseline:
- ≥ 2× detection rate on low-texture surfaces
- jitter < 2 px RMS when the phone is held still
- ≥ 20 fps on the budget Android

## Licenses (checked 2026-11-22)
| Component | License | Note |
|---|---|---|
| XFeat (verlab/accelerated_features) | Apache-2.0 | chosen detector |
| LightGlue / LighterGlue (cvg) | Apache-2.0 (code + weights) | |
| SuperPoint weights | non-commercial | **avoided** |
| OpenVINS | GPL-3.0 | Phase 3 candidate only if GPL is acceptable |
| MindAR | MIT | baseline |

## Repo layout
```
bench/       capture page (video + IMU + frame timestamps), evaluation scripts, reports
tracker/     model export (ONNX), homography/pose, filters, gyro fusion
web/         browser demo (next generation of artarget)
research/    dated notes: papers, experiments, results
docs/        roadmap, case study for portfolio
```

## Phase 0 — how to record a test clip
1. Open `bench/capture/` on the phone (via GitHub Pages, HTTPS).
2. Allow camera + motion sensors, enter phone model and surface name.
3. Record 20–30 s: 5 s still, slow circle around the surface, quick shake, move away and back.
4. Two files download: `*.webm|mp4` (video) and `*.json` (IMU samples, frame timestamps, camera settings).

---
Author: Behrang Mazloumi · Part of [Behrang Lab](https://ecoartic.github.io/opuscar-studio/)
