# 2026-11-22 — Quick map from 4 marked rectangle corners (idea: Behrang)

User marks the 4 corners of the desk top (fixed colour per physical corner) in 2+ views and enters the real size (measured: 120 × 60 cm, height 71 cm).

## Method (`mapping/quickmap.js`, runs in the browser with OpenCV.js)
1. **Focal length** — grid search (0.25–2.2 × long side, log) + golden-section refinement of the mean corner reprojection error of all 4-corner views (planar PnP, IPPE). No calibration needed → works on any phone.
2. **Pose** per view: IPPE (4 corners) or SQPNP (3 corners). Handedness auto-fix (cameras must be above the desk).
3. **Map**: ORB (CLAHE, 1500–2000) per view; **epipolar-guided matching** (F from the known poses, ±4 px then ±3 px) → DLT triangulation → reprojection < 3–4 px, parallax > 1.7°.
4. **Bundle-lite**: each view's pose re-estimated from its triangulated points + corners (×8 weight), then matching again (2 iterations).
Output uses the same map format/runtime as `armap.html` (metric, desk frame: origin front-left corner, X front edge, Y back, Z up).

## Validation against the COLMAP map of the same video (synthetic clicks = projected desk corners + 1.5–2 px noise)
| Views | Focal (gt 188.5 px @480) | Camera centre error | 3D points | Time |
|---|---|---|---|---|
| 3 (wide baselines) | 190.0 (+0.8 %) | 2.1–3.3 cm | 240 | 1.5 s (node) |
| 7 | 186.2 (−1.2 %) | 0.8–2.4 cm (one view 8 cm) | 2,531 | 5.7 s (node) |
Browser end-to-end (7 views → AR on fake camera from the same video): map built in **2.9 s**, 1,802 points, corner rms 1.3 px, **localized 50/50** samples; desk outline drawn in AR lands on the desk.

## Findings
- Measured desk height 71 cm → COLMAP map scale 0.1147 m/unit; desk-top extent measured *from the map* 1.13 × 0.59 m vs real 1.20 × 0.60 m → metric map confirmed within ~5 %.
- Estimated FOV 104° (long side) ⇒ Chrome on the M13 opened the **ultra-wide** camera ("camera 2"). Fine for mapping (more context), but lower resolution per degree; consider choosing the main camera via deviceId.
- Not every view can show all 4 corners of a 1.2 m desk in portrait → UI allows 3-corner views and placing a corner in the grey margin outside the frame along the edge lines; at least one 4-corner view is required for the focal estimate.
