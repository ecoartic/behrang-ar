# 2026-11-22 — First real capture: Samsung Galaxy M13, rug (Tested)

Files: `bench/results/2026-11-22_samsung-m13_rug.*` (video kept off-repo).
Android 10 build UA, Chrome 157, back camera "camera 2", 720×1280 portrait, 14.7 s.

## Findings
| Metric | Value | Meaning |
|---|---|---|
| Real camera rate (captureTime) | **24.5 fps** (requested 30) | indoor auto-exposure lengthens frames |
| Capture interval sd / p95 | 11.8 ms / 54.7 ms | uneven exposure timing |
| Real dropped frames (presentedFrames) | **2 / 360** | pipeline itself keeps up |
| Callback jitter | 18.3 ms sd | mostly 60 Hz display quantization, not camera — use captureTime |
| Capture→JS latency spread | mean +20 ms, max +50 ms | pose prediction needed for steady overlay |
| IMU | **none** (devicemotion and deviceorientation both silent) | blocker for gyro fusion |
| Camera controls exposed to web | exposureTime (0.065–142 ms), ISO 40–2500, focus, zoom | manual shutter is possible from the browser on this phone |
| Sharpness | median 227, 6% frames blurry | fine |
| ORB keypoints | median 997, min 690 | rug+objects scene is texture-rich |
| LK+RANSAC inlier ratio | median 0.995, p10 0.969, weak frames 0% | frame-to-frame tracking trivially easy here |

## Conclusions
1. The budget phone is **not** the bottleneck for frame-to-frame tracking on textured scenes; the hard parts are (a) re-detection after loss, (b) low-texture surfaces, (c) latency/jitter of the overlay.
2. `captureTime` from requestVideoFrameCallback is available on Chrome Android → we can timestamp frames on the camera clock and align IMU without guessing.
3. Manual exposure via `applyConstraints` is exposed → lock shutter (~1/120 s) to hold 30 fps and cut blur. Added as an option in the capture page (bench@2).
4. Missing IMU must be diagnosed before Phase 1. Capture page now shows live sensor Hz before recording, checks the Permissions API, and falls back to the Generic Sensor API (`Gyroscope`, `LinearAccelerationSensor`).

## Next captures needed
- Same phone, after enabling Chrome → Site settings → Motion sensors; with and without shutter lock.
- Low-texture surfaces: white table, plain wall, glossy table — these decide Phase 1 success.
