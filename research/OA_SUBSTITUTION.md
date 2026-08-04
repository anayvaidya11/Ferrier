# Open-Access Substitution Work-Order (D-031) — P-06 / P-07

Committed 2026-08-04. Governing decision: DECISIONS D-031. **Status declaration:
every entry below is an UNVERIFIED lead except the items in §3 marked directly
verified. Nothing in this file strikes, revises, or satisfies any caveat — only
Stage B page-verification (§4–§5) can do that, per the NO_HARDWARE source-integrity
rule (a summarizer's output is never a source; numbers land in committed documents
only from pages read directly).** Stage A (this document + the D-031 ledger edits)
records the decision and the work-order; Stage B executes it in any session with
open egress to the hosts below — confirmed reachable from the local session on
2026-08-04 (PMC, MIT DSpace, MIT OCW, GitHub), so Stage B needs no cloud wait.

---

## 1. Whitney slot (P-06) — supplement with an OA pair; keep the 1982 DOI as the named tradition

No single OA source replaces Whitney 1982's four-component bundle. Coverage map:

| Component of Whitney 1982 | OA coverage |
|---|---|
| (a) mating force-equilibrium conditions | W1 (same author restating), W2, W3 |
| (b) wedging + jamming conditions / F–M parallelogram | W1, W2, W3, W4 |
| (c) RCC parameter selection | W1 (partial W7) |
| (d) experimental validation | **none — no OA substitute exists**; P-06's residual optional ask |

Fetch order (Stage B stops at the first pair that page-verifies for (a)–(c)):

| # | Source | Access | Status |
|---|---|---|---|
| W1 | **MIT OCW 2.875 (Fall 2004) "Rigid Part Mating" lecture PDF — taught by D. E. Whitney himself** — `https://ocw.mit.edu/courses/2-875-mechanical-assembly-and-its-role-in-product-development-fall-2004/6abbc6934125042e12e9d153f87f9278_cls3_rgd_prt_mn4.pdf` (Fall 2002 mirror: dspace.mit.edu/handle/1721.1/35795) | CC BY-NC-SA | URL confirmed in OCW search listing 2026-08-04; content unread — lead |
| W2 | **CJME 2025 OA review, "Advances in Robotic Peg-in-Hole Assembly"** — DOI 10.1186/s10033-025-01349-w, SpringerOpen | CC BY | lead (cloud-session research; unfetched) |
| W3 | **Simunovic 1979 Sc.D. thesis, "An information approach to parts mating," MIT** — dspace.mit.edu/handle/1721.1/16229; PDF bitstream `07c7c54f-e147-4db7-ba65-b81a4d124c31` | MIT DSpace open | **PDF download directly verified 2026-08-04** (HTTP 200, application/pdf, 9.65 MB); content unread — foundational Draper-era parts-mating analysis |
| W4 | **Zhang et al. 2019, "Peg–hole disassembly using active compliance," R. Soc. Open Sci. 6:190476** — PMC6731726 | CC BY | strong lead (WebFetch digest 2026-08-04: full text on PMC, quasi-static single peg-hole two-point-contact analysis, builds on Whitney 1982 as ref [14]) — digest only, page-verify at Stage B |
| W5 | Goli et al. 2024, dual peg-hole jamming, Proc. R. Soc. A 480:20230364 | OA status unconfirmed | lead; dual-peg (adjacent, not foundational) |
| W6 | U. Birmingham thesis (disassembly compliance) | repository | lead |
| W7 | PFA RCC application manual | vendor PDF | lead; RCC parameter practice |
| W8 | DTIC Draper/NSF part-mating progress reports | DTIC (403s bots; try curl) | leads; accession numbers unconfirmed |

**Honest gap:** component (d) has no OA substitute. P-06's human ask narrows to the
1982 full text for its experimental-validation content only — optional, needed only
if an IS8-17-driven T5-promotion argument wants it (D-027). The C-12 prior-art
citation of the 1982 DOI stands regardless (metadata citation of a named tradition).

## 2. Kallwies slot (P-07) — replace; obtain-the-PDF ask dropped

Rationale (D-031): (i) settled retrieval negative — nine dead routes (eight from
2026-08-02, plus the Kalaitzakis author-copy route checked dead by the 2026-08-04
cloud planning session: publications page carries DOI links only); (ii) the §3
reproduction caution; (iii) the abstract's figures were never the quantity #40
needs — 0.017 px is the authors' *improved* method and 0.17 px is OpenCV
cornerSubPix, neither is stock-AprilTag corner σ — so the current swept class value
σ_px ∈ {0.3, 0.5, 1.0} px is not obviously wrong against the OpenCV figure and the
paper, even obtained, would not have directly anchored #40.

Fetch order:

| # | Source | Access | Status |
|---|---|---|---|
| K1 | **Adámek et al. 2023, "Analytical Models for Pose Estimate Variance of Planar Fiducial Markers for Mobile Robot Localisation," Sensors 23(12):5746** — PMC10300747 / MDPI | CC BY 4.0 | strong lead (WebFetch digest 2026-08-04: closed-form variance formulas σ² as functions of normalized marker area and view angle — the quantity #40 consumes directly, skipping σ_px→pose propagation). **Known caveat: experimental basis is ArUco (5×5, 112 mm), not AprilTag 36h11** — Stage B check B3 gates whether it anchors the functional form only, with magnitudes staying swept/MR-measured (the repo's form-vs-magnitude discipline, cf. D-019/D-023) |
| K2 | **Abbas et al. 2019, "Analysis and Improvements in AprilTag Based State Estimation," Sensors 19(24):5480** — PMC6960891 / MDPI | CC BY 4.0 | strong lead (WebFetch digest 2026-08-04: experimental AprilTag pose error vs distance 30–70 cm and yaw 70–110°, variance data, GP-based error model). Ranked after K1: empirical magnitudes as cross-check; K1's closed forms fit #40's model better |
| K3 | Ryu et al., CVPR 2026 (openaccess.thecvf.com) | CVF open | lead |
| K4 | Laurent & Sandoz, FMAC, arXiv:2601.07723 | arXiv | lead |
| K5 | Richardson AprilCal | open | **flagged weak/risky** — calibration reprojection conflates corner noise with model error; use only with that caveat stated |
| K6+ | remaining cloud-session leads | various | walk only if K1–K4 all fail, logging dated failures |

Residual gap either way: measured-on-this-system covariance — already covered by the
MR bench `reproj_rms_px` column (the designed replacement path regardless; the
curve-swap protocol governs any run-time change).

## 3. Directly verified findings (the only non-lead content in this file)

1. **Reproduction caution — github.com/UniBwTAS/apriltags_tas/issues/4.** Body
   fetched raw via GitHub API 2026-08-04 (not a digest). Facts: opened 2021-06-18,
   still open, 8 comments; an independent user running the authors' published
   `refineCornerPointsByDirectEdgeOptimization` on the authors' own dataset (image
   `0019.png`, random.zip) could not reproduce the paper's 0.017 px median corner
   error — the cloud session's page-read of the thread records ≈0.70–0.71 px (~40×).
   **Not peer-reviewed. Usable as caution only; never a CLAIMS source.**
2. **0.017 / 0.17 px semantics** (from the paper's public abstract): 0.017 px is the
   authors' improved edge-refinement method; 0.17 px is OpenCV cornerSubPix; neither
   is stock-AprilTag corner σ.
3. **Simunovic thesis PDF accessibility** — HTTP header check 2026-08-04: 200,
   `application/pdf`, 9,652,252 bytes, `06451145-MIT.pdf` (infrastructure
   verification only; content unread).
4. **Egress check 2026-08-04 (local session):** PMC, MIT DSpace, MIT OCW, GitHub all
   reachable; royalsocietypublishing.org and DTIC 403 automated fetchers (retry with
   plain curl at Stage B).

WebFetch answers in §1–§2 are summarizer digests — leads, not sources, per
NO_HARDWARE's source-integrity rule.

## 4. Stage B extraction protocol

Page-read only: download the PDF, read the pages directly (Read tool), extract
text/table-sourced values with page/table/section cited per value. Figure-only
quantities are listed as gaps, not estimated. Automated fetch digests and search
snippets are leads and are discarded at citation time. Same protocol as the
2026-08-02 perception-prior pass, including its discard-the-digest precedent.

## 5. Stage B checklist (runs in any open-egress session — the local session
qualifies as of 2026-08-04; no cloud dependency)

- **B0** Confirm egress to the §1/§2 hosts (done for the local session 2026-08-04).
- **B1** Fetch and page-verify W1 + W2 (W3/W4 as reinforcement, optional).
- **B2** On W-pair verification: INTERFACE_SPEC §2.3 *appends* the OA citations,
  keeping the paywall clause verbatim; studies/H04 gains Addendum-only note A5;
  CLAIMS C-12's caveat is *revised* to cite the OA pair for theory content — struck
  entirely only if the 1982 full text itself lands (see the C-12 note).
- **B3** Fetch and page-verify K1 (Adámek). Check: does its variance model cover
  36h11-class square fiducials at IS §9 geometry, or ArUco-only? Decide
  form-anchor vs full-anchor accordingly, in writing.
- **B4** If K1 verifies: add as Paper 5 in `research/data/perception_prior.md` with
  a full extraction table. Any #40 anchoring goes through the ROADMAP curve-swap
  protocol only: a NEW registered curve set, before/after both reported;
  `params.py` / `test_params.py` row 40 changes only with a recorded revision; the
  C-14 phrasing rule stands ("swept across the plausible range", never
  "literature-derived curves").
- **B5** Else walk K2–K6 in order, logging dated failures in this file.
- **B6** Only after B1–B5: update HOLES H-07 note, C-14, and the PENDING_HUMAN rows
  per their written terms.
- **B7** Re-run the Stage A verification greps, inverted where a caveat was
  legitimately revised.

## 6. Standing rules inherited

NO_HARDWARE source-integrity rule (read the pages; digests are leads);
MASTER_CONTEXT §4.3 labeling; CLAIMS C-14 phrasing rule; amendments-win precedence;
curve-swap protocol (ROADMAP) for any mid-experiment input change.
