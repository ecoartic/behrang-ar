#!/usr/bin/env python3
"""Phase 0: sensor / timing / image-quality report for a bench capture.

Usage:
  python bench/eval_capture.py capture.json [--video capture.mp4]

Timing is measured from the camera's own timestamps (captureTime / mediaTime),
not from requestVideoFrameCallback arrival, because callback arrival is
quantized to the display refresh (60 Hz → 16.7 ms steps) and is not camera jitter.
Real drops come from gaps in presentedFrames.

With --video (needs opencv-python): sharpness (Laplacian variance), ORB keypoints,
and frame-to-frame Lucas-Kanade + RANSAC homography inlier ratio as a first
"trackability" baseline.
"""
import json, sys, statistics as st, argparse


def pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(len(xs) * p))]


def timing(d):
    F = d["frames"]
    out = {"frames": len(F)}
    cap = [f[3] for f in F if f[3] is not None]
    if len(cap) > 2:
        dc = [b - a for a, b in zip(cap, cap[1:])]
        out["capture_fps"] = 1000 / st.mean(dc)
        out["capture_interval_sd_ms"] = st.pstdev(dc)
        out["capture_interval_p95_ms"] = pct(dc, .95)
        lat = [f[0] - f[3] for f in F if f[3] is not None]
        m = min(lat)
        out["latency_spread_ms"] = {"mean": st.mean(lat) - m, "sd": st.pstdev(lat), "max": max(lat) - m}
    else:
        mt = [f[1] for f in F]
        dm = [(b - a) * 1000 for a, b in zip(mt, mt[1:])]
        out["capture_fps"] = 1000 / st.mean(dm)
        out["capture_interval_sd_ms"] = st.pstdev(dm)
    pf = [f[2] for f in F]
    out["dropped_frames"] = sum(max(0, b - a - 1) for a, b in zip(pf, pf[1:]))
    cb = [f[0] for f in F]
    out["callback_interval_sd_ms"] = st.pstdev([b - a for a, b in zip(cb, cb[1:])])
    out["duration_s"] = (cb[-1] - cb[0]) / 1000
    return out


def imu(d):
    I = d["imu"]
    if len(I) < 3:
        return None
    t = [r[0] for r in I]
    di = [b - a for a, b in zip(t, t[1:])]
    gyro = sum(1 for r in I if r[7] is not None)
    return {"source": d.get("imuSource"), "rate_hz": 1000 / st.mean(di), "interval_sd_ms": st.pstdev(di),
            "samples": len(I), "gyro_samples": gyro}


def video(path):
    import cv2
    cap = cv2.VideoCapture(path)
    orb = cv2.ORB_create(1000)
    prev = pts = None
    sharp, kps, ratio = [], [], []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        h, w = f.shape[:2]
        s = 640 / max(h, w)
        g = cv2.cvtColor(cv2.resize(f, (int(w * s), int(h * s))), cv2.COLOR_BGR2GRAY)
        sharp.append(cv2.Laplacian(g, cv2.CV_64F).var())
        kps.append(len(orb.detect(g, None)))
        if prev is not None and pts is not None and len(pts) >= 8:
            p1, stt, _ = cv2.calcOpticalFlowPyrLK(prev, g, pts, None)
            ok_ = stt.ravel() == 1
            if ok_.sum() >= 8:
                _, m = cv2.findHomography(pts[ok_], p1[ok_], cv2.RANSAC, 3.0)
                ratio.append((m.sum() if m is not None else 0) / len(pts))
            else:
                ratio.append(0)
        pts = cv2.goodFeaturesToTrack(g, 1000, 0.01, 5)
        prev = g
    return {"frames": len(sharp), "sharpness_median": st.median(sharp), "sharpness_p10": pct(sharp, .1),
            "blurry_frames_pct": 100 * sum(1 for x in sharp if x < 100) / len(sharp),
            "orb_kp_median": st.median(kps), "orb_kp_min": min(kps),
            "lk_inlier_ratio_median": st.median(ratio), "lk_inlier_ratio_p10": pct(ratio, .1),
            "lk_weak_frames_pct": 100 * sum(1 for x in ratio if x < .5) / max(1, len(ratio))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json")
    ap.add_argument("--video")
    a = ap.parse_args()
    d = json.load(open(a.json))
    s = d["camera"]["settings"]
    rep = {"device": d.get("device"), "surface": d.get("surface"), "schema": d.get("schema"),
           "resolution": f'{s.get("width")}x{s.get("height")}', "requested_fps": s.get("frameRate"),
           "shutter_lock": d.get("shutterLock"), "timing": timing(d), "imu": imu(d)}
    caps = d["camera"].get("capabilities") or {}
    rep["camera_controls"] = {k: (k in caps) for k in ("exposureTime", "iso", "focusDistance", "torch", "zoom")}
    if a.video:
        rep["video"] = video(a.video)
    v = []
    t = rep["timing"]
    if t["capture_fps"] < (s.get("frameRate") or 30) * 0.9:
        v.append(f'camera delivers {t["capture_fps"]:.1f} fps (< requested) → auto-exposure lengthening frames; try shutter lock')
    if t["dropped_frames"] > 3:
        v.append(f'{t["dropped_frames"]} dropped frames')
    if not rep["imu"] or not rep["imu"]["gyro_samples"]:
        v.append("no gyro data → fix sensor permission before Phase 1 gyro fusion")
    if a.video and rep["video"]["blurry_frames_pct"] > 20:
        v.append(f'{rep["video"]["blurry_frames_pct"]:.0f}% blurry frames')
    rep["verdict"] = v or ["OK for Phase 1"]
    print(json.dumps(rep, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
