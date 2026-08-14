# P-03 shopping list — instruments only (NO_HARDWARE rev 2)

Every row passed the three-question test in `MEASUREMENT_REQUESTS.md`
(1: a committed decision depends on the number; 2: consumed by the
experiment; 3: discarded/repurposed after). No camera hardware — the
user's iPhone + a manual-exposure app serves (MR-001: "zero if an owned
device serves"). Order of magnitude total: **$50–150**.

| Item | Spec that matters | Est. cost |
|---|---|---|
| Manual-exposure camera app | Locks shutter + ISO for **video**, shows the values (Blackmagic Camera: free; Halide is stills-only) | $0 |
| Lux-meter app | Reads illuminance at the tag plane; relative accuracy suffices | $0 |
| Tripods × 2 | One for the board, one for the phone; any $15-class phone tripod + any board-holding stand/clamp | $30–60 |
| Phone tripod mount/clamp | Holds the iPhone rigid (capture must be hands-off) | $8–15 |
| Dimmable lamp | Smooth dimming to near-dark for the MR-002 {1–50} lux sweep; a dimmer + warm bulb is fine | $15–30 |
| Matte paper, heavyweight | Non-gloss (glare kills the detector honestly but unrepeatably); print S1 ×4+, S2 ×2, S3 ×2, S4 ×1 | $5–10 |
| Rigid board | Foam board or plywood scrap, ≥ 350 × 500 mm, flat | $5–10 |
| Spacers ≥ 2, arbitrary heights | Shop-bought as-is (PVC caps / wood blocks / stacked washers). **Never cut to a dimension** | $5 |
| Soil + water + mixing container | MR-001 mud; any soil | $0–5 |
| Tape measure + protractor | Range and view-angle setting (consumer precision is acceptable per MR-001) | $10 |
| Painter's tape | Mount sheets without wrecking them between conditions | $5 |

**Print settings reminder:** 100% / "Actual Size", matte paper, then check
each sheet's scale bar = 100 ± 1 mm before building the rig.
