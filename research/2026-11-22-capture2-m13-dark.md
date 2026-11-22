# 2026-11-22 — Capture 2: Samsung M13, rug, very low light, shutter locked 1/120

Files: `bench/results/2026-11-22_samsung-m13_rug_shutter.*`

## Results
| Metric | Capture 1 (auto exposure, room light) | Capture 2 (1/120 locked, very dark) |
|---|---|---|
| Real fps | 24.5 | 26.6 |
| Dropped frames | 2 | **41** |
| Capture→JS latency (max spread) | 50 ms | 74 ms |
| Sharpness (median) | 227 | **2.2** (image almost black) |
| ORB keypoints (median) | 997 | **7** |
| IMU | none | **devicemotion 56 Hz, accelerometer only** |
| Gyro (rotationRate) | – | **null in all 862 samples** |

## Conclusions
1. **Motion sensors work after enabling Chrome site permission**, but this phone reports no rotationRate → it almost certainly has **no gyroscope** (common on budget Galaxy A/M models). Without a gyro, ARCore cannot run on it at all — this is exactly the class of device the project targets.
2. → Phase 1 must be **vision-only tracking**; the accelerometer still gives the gravity vector (pitch/roll prior for the surface plane, ~56 Hz).
3. A fixed short shutter without ISO control in low light makes the image unusable. Fixed exposure is wrong; need **adaptive exposure**: cap shutter at 1/60 for blur, raise ISO first, allow 1/30 only when ISO is maxed.
4. Capture page bench@3: exposure modes (auto / smart / lock 1/120), smart mode measures luminance at 2.5 Hz and drives ISO + shutter via applyConstraints, logs `expoLog`; gyro presence detected explicitly, Generic Sensor `Gyroscope` tried when devicemotion has no rotationRate.
   - Not testable headless (fake camera exposes no manual exposure) → needs a phone test.

## Next
- Same phone, normal room light: smart exposure vs auto, same rug → compare blur + fps.
- Low-texture surfaces (white table) with smart exposure.
- Any phone **with** a gyro (for the fusion path).
