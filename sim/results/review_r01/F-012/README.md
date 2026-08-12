# F-012 probe — Q_NOMINAL is Ry(180°); IS §4/§7 pin nominal at Rz(180°)

Run: `sim/.venv/bin/python studies/R01_PHASE1_REVIEW/probes/probe_f012.py`
(N=50 nominal trials per arm, local MuJoCo, D-032-rule seeds from
sweep_root 20260811).

**Verdict: CONFIRMED** — all 10 checks true. Arm A (frozen (0,0,1,0)):
outer tag z = −0.185 m in head_frame every trial; cam A view angle ≈37.7°
at 300 mm, ≈62.4° at handoff. Arm B (Rz(180) control): +0.185 m, ≈6.1°,
≈14.8°. The IS §4 constraint set {+X anti-parallel, +Z plate-up ∥ +Z
head-up at level attitude, right-handed} is satisfied uniquely by
Rz(180°).

**Nuance for the ratification sitting:** outcome census is success 50/50
in BOTH arms at the nominal cell — clean-condition detection saturates, so
the inversion's contamination concentrates in the degraded bands (where
the cos^n angle factor bites), i.e. exactly the D-029 gate cell. The
frozen clean-condition ~89% is likely robust; the frozen moderate-band
numbers are not.
