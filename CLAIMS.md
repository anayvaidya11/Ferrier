# Claims Register

Every claim WyZen makes externally — proof site, deck, application, video, conversation
— gets a row here **before it is made**: the claim, the committed evidence, the §4.3
label, and a status: **EVIDENCED** (primary evidence committed), **PARTIAL** (derived
or secondary support; stated gaps), **ASSERTED** (no committed evidence yet — may not
be used externally without its caveat attached). A claim with no row is not made. If
the repository and a published claim disagree, the repository is right (§4.3).
A register whose every row reads EVIDENCED is a register nobody audited.

| # | Claim | Evidence | Label | Status |
|---|---|---|---|---|
| C-01 | The Army asked industry, in writing, for autonomous recovery of disabled vehicles under DDIL (June 2026 RFI) | `research/RFI_ACC-APG.md` — full notice verbatim via SAM.gov API, corroborated | sourced (primary) | **EVIDENCED** |
| C-02 | No funded recovery program exists yet — the RFI is AAL market research; recovery is not a named prototype mission set | `research/FOLLOW_ON.md`; A-008 | sourced (primary) | **EVIDENCED** |
| C-03 | Five vendors selected for Project Sustainment, July 2026, via NAMC | `research/VENDORS.md` — three independent sources | sourced | **EVIDENCED** |
| C-04 | MIL-STD-3078 and STUB standardize nothing platform-side; a recovery/docking interface is genuine white space | `research/STANDARDS.md` — MIL-STD-3078 read in full; MIL-PRF-32383/7 **not** retrieved | sourced (primary) + one gap | **PARTIAL** — gap named in STANDARDS UNVERIFIED |
| C-05 | Latch tension rating 15 kN | D-003-R(a) | assumed | **ASSERTED** — unverified until Phase 2 |
| C-06 | Stud neck bending governs; 462 N·m design moment, SF ≈ 2.2 at the ±20° sector edge | D-003-R(b); INTERFACE_SPEC §2.1 derivation | derived (class-value inputs) | **PARTIAL** |
| C-07 | Mud degrades detection per the D-023 model | D-023 | extrapolated | **ASSERTED** pending MR-001 |
| C-08 | Camera parameters (1920×1200 global-shutter mono, stated FOVs/extrinsics) | D-012, D-025 | assumed | **ASSERTED** |
| C-09 | "Simulation shows meaningful value at a 40% autonomous success rate" (MASTER_CONTEXT §1.5) | **none — no committed simulation exists today** | asserted | **ASSERTED — flagged: this §1.5 sentence currently has no evidence behind it; Phase 1's D-014 curve is what could evidence it, and until then it must not be used externally** |
| C-10 | A standardized interface converts open-ended grasping into constrained docking (§1.2 thesis) | studies/H08 (structural derivation), STANDARDS white space, drone-dock precedent (unfetched) | derived + literature framing | **PARTIAL** — Phase 1 measures it |
| C-11 | Useful before it's perfect — refusal is cheap, wrong insertion is expensive | §1.5 argument; D-017's tradeoff curve is the quantitative form | asserted | **ASSERTED** until the D-017 curve exists |
