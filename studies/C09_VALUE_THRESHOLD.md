# C-09 — The Value Threshold, Derived

**What this is:** the mission-level trade model that replaces MASTER_CONTEXT §1.5's
unsourced sentence "Simulation shows meaningful value at a 40% autonomous success
rate" (CLAIMS C-09 — flagged circular: Phase 1's simulation is the thing that would
show it). This is **arithmetic about trip counts and risk exposure, not physics and
not simulation** — Phase 0-legal, label **derived, with every input a swept class
parameter; no empirical casualty, attrition, or timeline data is used or implied.**

## 1. The decision being modeled

An unmanned asset is disabled forward. Two policies:

- **Policy H (status quo):** a human recovery team goes immediately.
- **Policy R (robot-first):** the recovery robot goes; with probability P it succeeds;
  on failure, humans go — the fallback is exactly the status quo (§1.5).

## 2. Symbols — all class parameters, all swept

| Symbol | Meaning |
|---|---|
| P | Probability the robot sortie recovers the asset (the Phase 1 number) |
| S_h | Expected human-sortie risk cost: team size × per-sortie casualty risk × cost of a casualty |
| a·V_r | Expected robot-sortie attrition cost: loss probability × robot value |
| V_a | Value of the disabled asset |
| λ | Hazard rate of losing the asset while it sits (enemy action, weather, capture) |
| T_r, T_h | Robot / human sortie timelines |

## 3. Derivation

Expected costs (linearized hazard, L(T) = λT):

- E_H = S_h + λT_h·V_a
- E_R = a·V_r + (1−P)·S_h + V_a·λ·[P·T_r + (1−P)(T_r + T_h)]

Policy R beats Policy H when E_R < E_H. Expanding the bracket:
P·λT_r + (1−P)λT_r + (1−P)λT_h = λT_r + (1−P)λT_h, so

E_R − E_H = a·V_r − P·S_h + V_a·λ·(T_r − P·T_h) < 0

**⟹ P > P\* = (a·V_r + λ·T_r·V_a) / (S_h + λ·T_h·V_a)**

**In words: the robot needs a success probability exceeding the ratio of what its
sortie risks to what a human sortie risks.** That is "useful before it's perfect,"
quantified: the threshold is not an accuracy bar, it is a risk ratio — and the entire
company premise (§1.3, §1.5) is that this ratio is well below one, because the robot
is expendable-class materiel and the soldiers are not.

Dimensionless form (divide by S_h): with ρ = a·V_r/S_h (robot-to-human sortie risk
ratio) and h = λT_h·V_a/S_h (asset-hazard-to-casualty ratio), assuming comparable
timelines T_r ≈ T_h:

**P\* = (ρ + h) / (1 + h)**

## 4. The threshold across the swept region

| | h = 0 | h = 0.2 | h = 0.5 |
|---|---|---|---|
| ρ = 0.05 | **5%** | **21%** | **37%** |
| ρ = 0.10 | **10%** | **25%** | **40%** |
| ρ = 0.20 | **20%** | **33%** | **47%** |
| ρ = 0.40 | 40% | 50% | 60% |

**Reading:** a 40% docking success rate clears the threshold across the region where
the robot sortie risks ≲ 25–35% of what the human sortie risks (in casualty-
denominated terms), including under substantial asset-hazard pressure. It fails only
where the robot sortie approaches half a human sortie's risk cost — at which point the
robot is mis-priced for the mission, not the autonomy under-performing.

## 5. What may and may not be claimed (feeds CLAIMS C-09)

- **Permitted, with this study cited:** "A mission-level trade model shows robot-first
  recovery beats sending soldiers whenever docking success exceeds the robot-to-human
  sortie risk ratio — of order 10–35% across the swept parameter region. Phase 1
  measures whether the system clears it." Label: derived, swept class parameters.
- **Retired, may not be used:** "Simulation shows meaningful value at a 40% success
  rate." No simulation has shown anything yet; §1.5 is amended accordingly (A-010).
- The model is denominated in casualty exposure, consistent with §1.5's rule: the
  materiel argument can invert if UGVs get cheap; the casualty argument does not, and
  ρ inherits that robustness because S_h sits in its denominator.

## 6. Limits, stated

Static two-policy, single-asset, single-sortie model; linearized hazard; excludes
robot reuse across many sorties (favorable, omitted conservatively), fleet-level
tempo/deterrence effects, and the D-017 asymmetry *within* a sortie (wrong-insertion
damage risk — priced separately by the refusal/damage tradeoff curve). No input is
empirical; every input is a swept ratio. If someone supplies sourced values for any
symbol, the table narrows honestly — file them as inputs, never assert them.
