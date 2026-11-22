#!/usr/bin/env python3
"""Phase 0: sensor/timing quality report for a bench capture (.json from bench/capture).

Usage: python bench/eval_capture.py capture.json [more.json ...]
Reports per device: real camera fps, frame-interval jitter, dropped frames,
IMU rate and jitter, and whether gyro data exists (needed for gyro fusion).
"""
import json, sys, statistics as st

def stats(xs):
    if len(xs) < 2: return None
    return dict(mean=st.mean(xs), sd=st.pstdev(xs), p95=sorted(xs)[int(len(xs)*.95)-1], max=max(xs))

def report(path):
    d = json.load(open(path))
    fr = [f[0] for f in d["frames"]]
    fi = [b - a for a, b in zip(fr, fr[1:])]
    imu = [r[0] for r in d["imu"]]
    ii = [b - a for a, b in zip(imu, imu[1:])]
    gyro = sum(1 for r in d["imu"] if r[7] is not None)
    s = d["camera"]["settings"]
    f, i = stats(fi), stats(ii)
    dur = (fr[-1] - fr[0]) / 1000 if len(fr) > 1 else 0
    exp = s.get("frameRate") or 30
    dropped = sum(max(0, round(x / (1000 / exp)) - 1) for x in fi)
    print(f"\n== {d.get('device') or '?'} | {d.get('surface')} | {s.get('width')}x{s.get('height')} | {dur:.1f}s")
    if f: print(f"  camera: {1000/f['mean']:.1f} fps  interval sd {f['sd']:.2f} ms  p95 {f['p95']:.1f} ms  dropped≈{dropped}")
    if i: print(f"  IMU:    {1000/i['mean']:.0f} Hz  interval sd {i['sd']:.2f} ms  gyro samples {gyro}/{len(imu)}")
    else: print("  IMU:    none (desktop or permission denied)")
    verdict = []
    if f and 1000 / f['mean'] < 24: verdict.append("low fps")
    if f and f['sd'] > 8: verdict.append("unstable frame timing")
    if not i or gyro == 0: verdict.append("no gyro → no gyro fusion")
    print("  verdict:", ", ".join(verdict) or "OK for Phase 1")

for p in sys.argv[1:]: report(p)
