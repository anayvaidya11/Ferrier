# Perception Prior: Literature-Derived Fiducial Detection & Pose Accuracy Values

**Purpose:** Fills PHASE1_PARAMETERS #39 (detection-rate model anchors) and #40 (pose-covariance class values) with literature-derived numbers.

**Provenance label:** literature-derived, **text/table-sourced only**. This extraction pass deliberately did NOT read numeric values off plot curves or interpret figure imagery. Every figure-only quantity is listed as a gap in the "Not covered by this corpus" section rather than estimated. All values below were read from a document fetched on the retrieval date noted in each section.

**Status:** COMPLETE (text/table-only pass, 2026-08-02). Papers 1-3 fetched and page-verified; Paper 4 (Kallwies 2020) UNAVAILABLE — see UNVERIFIED section (settled negative per D-031; OA substitution pending — `research/OA_SUBSTITUTION.md`).

---
## Paper 1: Olson 2011 — AprilTag (ICRA)

**Citation:** E. Olson, "AprilTag: A robust and flexible visual fiducial system," Proc. IEEE Int. Conf. Robotics and Automation (ICRA), 2011.
**URL:** https://april.eecs.umich.edu/media/pdfs/olson2011tags.pdf
**Retrieved:** 2026-08-02 (PDF fetched and all 8 pages read directly this session).

### Extracted values (text / tables / captions only)

| # | Value | Where stated |
|---|-------|--------------|
| 1.1 | Visual fiducials in this paper span ~49 to 100 pixels *including* payload (QR alignment markers alone ≈ 268 px) | Sec. I (Introduction), body text |
| 1.2 | Recommended low-pass filter sigma = 0.8 before gradient clustering | Sec. III-A, body text |
| 1.3 | Clustering parameters K_D = 100, K_M = 1200 | Sec. III-A, body text |
| 1.4 | Quad-search "close enough" threshold = 2 x segment length + 5 px | Sec. III-B, body text |
| 1.5 | Corner estimates "accurate to a small fraction of a pixel" — QUALITATIVE ONLY, no number given | Sec. III-B, body text |
| 1.6 | Theoretical false-positive table, 36h10 vs 36h15, by bits corrected (%): 0 bits: 0.000001 / 0.000000; 1: 0.000041 / 0.000002; 2: 0.000744 / 0.000029; 3: 0.008714 / 0.000341; 4: 0.074459 / 0.002912; 5: 0.495232 / 0.019370; 6: N/A / 0.104403; 7: N/A / 0.468827 | Sec. V-B, in-text table ("Bits corrected / 36h10 FP (%) / 36h15 FP (%)") |
| 1.7 | Codebook sizes & min Hamming (in-text table): ARToolkit+ simple 36 bits / 512 codes / d=4; ARToolkit+ BCH 36 / 4096 / 2; ARTag 36 / 2046 / 4; Proposed 36h9 36 / 4164 / 9; Proposed 36h10 36 / 2221 / 10; 36h15 has only 27 codewords | Sec. V, in-text table + surrounding text |
| 1.8 | Using 16-bit tags instead of 36-bit tags gains only ~25% detection range (4-px border overhead dominates) | Sec. V, body text |
| 1.9 | False-positive evaluation corpus: LabelMe, 180,829 images | Sec. VI-A, body text |
| 1.10 | Complexity heuristic: tags with min rectangle-covering complexity < threshold (typically 10) rejected; at complexity c=9, c=10 empirical FP rate drops below the random-payload theoretical prediction; performance better than theory once complexity exceeds 8 | Sec. V + Sec. VI-A text and Fig. 6 caption |
| 1.11 | Synthetic localization experiments: ray-traced images at 400x400 resolution, pinhole lens, focal length 400 px | Sec. VI-B, body text |
| 1.12 | Example synthetic frame: tag at 10 m, normal 30.3 deg off camera axis | Fig. 8 caption |
| 1.13 | Range experiment (phi = 0, varying distance): "our detector works reliably to 50 m, while the ARToolkitPlus detector's detection rate drops to under 50% at around 25 m" | Sec. VI-B, body text (re Fig. 10) |
| 1.14 | Runtime: ~30 fps on VGA-resolution images, Intel Core2 2.6 GHz (Java) | Sec. VI-B, body text |

### Figure-only quantities in this paper — NOT extracted (text/table-only pass)
- Fig. 9: orientation error (deg) and detection rate vs off-axis angle 0–90 deg — the per-angle numeric curves are available only as a figure — not extracted (text/table-only pass). Caption is qualitative only ("dramatically lower localization error... detects targets more reliably").
- Fig. 10: range error (m) and detection rate vs target distance 0–80 m — curves available only as a figure — not extracted (text/table-only pass); only the 50 m / 25 m sentence in the text (row 1.13) is usable.
- Fig. 6 / Fig. 7: empirical false-positive-rate curves vs bit errors corrected — available only as a figure — not extracted (text/table-only pass).

**Interpretation caveat:** rows 1.11–1.13 come from *synthetic ray-traced* imagery; the paper itself warns real-world performance "will be lower than these synthetic experiments due to noise, lighting variation, and other non-idealities."

---
## Paper 2: Wang & Olson 2016 — AprilTag 2 (IROS)

**Citation:** J. Wang and E. Olson, "AprilTag 2: Efficient and robust fiducial detection," Proc. IEEE/RSJ Int. Conf. Intelligent Robots and Systems (IROS), 2016.
**URL:** https://april.eecs.umich.edu/media/pdfs/wang2016iros.pdf
**Retrieved:** 2026-08-02 (PDF fetched and all 6 pages read directly this session).

### Extracted values (text / tables / captions only)

| # | Value | Where stated |
|---|-------|--------------|
| 2.1 | Practice note: "No known users accept tags with more than two bit errors"; occluded tags usually have >= 1 bit error and most users disable bit-error decoding entirely because of false-positive impact | Sec. III-A, body text |
| 2.2 | Adaptive threshold: image divided into 4x4-px tiles, extrema over 3x3 tile neighborhood, per-pixel threshold = (max+min)/2 | Sec. III-B, body text |
| 2.3 | Quad prefilter rejects fits with corner angles deviating too far from 90 deg (no numeric tolerance given) | Sec. III-D, body text |
| 2.4 | Quick decode: bit-error correction limited to <= 2 bits, enabling O(1) hash lookup over O(n^2) precomputed codes | Sec. III-E, body text |
| 2.5 | **TABLE I (false positives, LabelMe, 421,049 images, AprilTag-36h11, up to 2 bit errors corrected; theoretical FP rate 0.000570%):** Old detector: 51,075,971 candidate quads, 145 false detections, FP rate 0.000284%. New detector: 13,623,725 candidate quads, 6 false detections, FP rate 0.000044% | Table I + caption |
| 2.6 | Localization experiments: ray-traced images, ideal pinhole camera; Exp. 1 varies distance with tag parallel to image plane; Exp. 2 fixes tag on optical axis and varies normal angle vs camera axis; both repeated with images decimated to half size | Sec. IV-B, body text |
| 2.7 | Real-image mosaic test: Point Grey Chameleon at 1296x964 px, each tag 0.167 m wide, distances 0.6 m (closest) to 7.0 m (farthest), rectification before detection, ground truth via laser tape measure | Fig. 8 caption + Sec. IV-B text |
| 2.8 | Real-data conclusion (qualitative): new detector detects "at the full range of distances" (to 7.0 m at that tag size/resolution) "while the old detector experiences a rapid fall-off in detection rate" | Sec. IV-B/IV-C boundary text (re Fig. 10) |
| 2.9 | Timing (LabelMe, single thread, Xeon E5-2640 2.5 GHz): new 0.254 us/px vs old 0.374 us/px = ~78 ms vs ~115 ms per 640x480 image; with 2x decimation new = 0.072 us/px = ~22 ms per 640x480 | Sec. IV-C, body text |

### Figure-only quantities in this paper — NOT extracted (text/table-only pass)
- Fig. 5: position error (m) vs distance (0-30 m, simulated) — available only as a figure — not extracted (text/table-only pass).
- Fig. 6: orientation error (deg) vs off-axis angle (0-90 deg, simulated; y-axis spans 0-3 deg) — per-angle values available only as a figure — not extracted (text/table-only pass).
- Fig. 7: % tags detected vs distance (0-50 m, simulated) — the detection-rate falloff curve is available only as a figure — not extracted (text/table-only pass).
- Fig. 9: estimated vs actual distance, real mosaic data (0-7 m) — available only as a figure — not extracted (text/table-only pass).
- Fig. 10: % tags detected vs distance, real mosaic data (0-7 m) — available only as a figure — not extracted (text/table-only pass).

**Interpretation caveat:** the strongest quantitative rows here (2.5, 2.9) concern false positives and timing; the detection-vs-distance and error-vs-angle behavior of AprilTag 2 is figure-only in this paper.

---
## Paper 3: Krogius, Haggenmiller & Olson 2019 — Flexible Layouts for Fiducial Tags (IROS)

**Citation:** M. Krogius, A. Haggenmiller, E. Olson, "Flexible Layouts for Fiducial Tags," Proc. IEEE/RSJ Int. Conf. Intelligent Robots and Systems (IROS), 2019. (AprilTag 3.)
**URL:** https://april.eecs.umich.edu/media/pdfs/krogius2019iros.pdf
**Retrieved:** 2026-08-02 (PDF fetched and all 6 pages read directly this session).

### Extracted values (text / tables / captions only)

| # | Value | Where stated |
|---|-------|--------------|
| 3.1 | New tag families: uramaki 41h12 = 9x9 cells, Hamming distance 12, 2115 tags; old maki 36h11 = 10x10 cells, 587 tags; 10x10 uramaki layout = 52 data bits, Hamming 13, 48,714 unique tags; circular 21h7 = 38 unique tags; larger circular family = 65,698 unique tags | Sec. IV-A body text (+ Fig. 2 caption: 41 and 52 data bits for outside-border layouts; 21 and 49 bits for circular) |
| 3.2 | uramaki layout adds 16 data bits regardless of tag size by moving one bit layer outside the border | Sec. III-A, body text |
| 3.3 | Decoding detail: 36h11 cell values read into 6x6 array, sharpened with 3x3 Laplacian kernel K = I + 0.25[[0,-1,0],[-1,4,-1],[0,-1,0]] before decode | Sec. III-D, body text + Eq. 5 |
| 3.4 | **Recursive-tag detection range anchor:** 90.2 x 90.2 cm doubly nested recursive tag detected over 0.08 to 16.15 +/- 0.03 m using a 640x480 image from a Raspberry Pi Camera Module V2 | Sec. IV-A, body text |
| 3.5 | FP evaluation corpus: LabelMe, 207,920 images; detector produced 6,090,028 candidate quads for the 41h12 family and 6,128,551 for 21h7; first 1500 tags of each 41h12 family and first 35 of each 21h7 family used | Sec. III-E, body text |
| 3.6 | **TABLE I (false positives vs bit errors corrected 0/1/2/3, LabelMe, 9x9 uramaki 41h12 layout):** Rectangle Complexity 0 / 1 / 8 / 99; Connected Components 0 / 0 / 11 / 105; Ising Energy 0 / 0 / 4 / 44; Expected if random bits 0.0 / 0.2 / 3.4 / 44.3 | Table I + caption |
| 3.7 | **TABLE II (same, circular 21h7 layout):** Rectangle Complexity 152 / 3273 / 40,462 / 303,028; Connected Components 131 / 3600 / 45,052 / 320,174; Ising Energy 85 / 1867 / 22,266 / 165,862; Expected if random 102.3 / 2147.9 / 21,479.1 / 136,034.0 | Table II + caption |
| 3.8 | Recall/speed dataset: 160 images maki 36h11 + 160 images uramaki 41h12; 1296x964 Point Grey Chameleon; 10 tags per family photographed at 20-160 cm in 20 cm increments; at each distance one face-on image + one rotated 45 deg; each tag printed 4 cm across outer limits | Sec. III-E, body text + Fig. 6 caption |
| 3.9 | Parameter sweep ranges: AprilTag 2 decimation 1-17; AprilTag 3 decimation 1-24; ArUco minMarkerSize 0-0.11 step 0.01; timing on Intel i7-7600U @ 2.80 GHz | Sec. III-E, body text |
| 3.10 | Qualitative comparisons: AprilTag 3 "is faster and has higher recall than both the AprilTag 2 and ArUco detectors"; recall differences between detectors are "mostly due to differences in the distance at which the detector begins failing to detect tags"; when tuned for max recall, 41h12 ~ equivalent to 36h11; at high decimation 41h12 recall < 36h11 (white background gives 36h11 an effectively larger border) | Sec. IV-C, IV-D body text |
| 3.11 | Ising-energy complexity metric performs best; for 21h7 it pushes empirical FP "even below the rate expected for a uniform random distribution of bits" | Sec. IV-B, body text |

### Figure-only quantities in this paper — NOT extracted (text/table-only pass)
- Fig. 7: recall vs frames-per-second (0-1200 fps) parameter sweep for AprilTag 3 (36h11, 41h12), AprilTag 2, ArUco — available only as a figure — not extracted (text/table-only pass).
- Fig. 8: recall vs tag distance (20-160 cm) for 4 cm tags at max-recall settings — the per-distance recall values are available only as a figure — not extracted (text/table-only pass). Caption is qualitative ("AprilTag 3 is capable of detecting tags at a greater distance than the other detectors").

**Interpretation caveat:** rows 3.4 and 3.8 jointly bound useful detection geometry: a 4 cm tag imaged at 1296x964 remains detectable at some substantial fraction of 160 cm (exact recall per distance is figure-only), while a 90.2 cm recursive tag spans 0.08-16.15 m at 640x480.

---
## Paper 4: Kallwies, Forkel & Wuensche 2020 — Localization Accuracy of AprilTag Detection (ICRA) — UNAVAILABLE

**Citation:** J. Kallwies, B. Forkel, H.-J. Wuensche, "Determining and Improving the Localization Accuracy of AprilTag Detection," Proc. IEEE ICRA, 2020, pp. 8288-8294. DOI 10.1109/ICRA40945.2020.9197427.
**Status:** UNAVAILABLE — no open-access PDF found; NO values extracted (nothing recorded from memory). See UNVERIFIED section for the full list of URLs tried.
**Impact:** this was the corpus's only source of quantified corner/edge localization accuracy in pixels (the paper's stated topic). Its absence leaves the pose-covariance class values unanchored by this pass.

---

## Proposed injected-model parameters

All entries below trace to an extracted row above. Where the text/table corpus is too thin to anchor a curve region, that is stated explicitly and the region is left to MR data — no shape has been invented.

### Detection-rate anchors (PHASE1_PARAMETERS #39)

- **D1 — near-field plateau (real imagery):** 0.167 m tags at 1296x964 detected by the AprilTag 2 detector across the full tested range 0.6-7.0 m ("detects tags at the full range of distances") → model detection rate as a plateau ~1.0 in this regime. Trace: rows 2.7, 2.8. NOTE: focal length is not stated in the paper's text, so this anchor cannot be converted to tag size in pixels from the text alone; it must be injected in metric+resolution form or converted using MR camera intrinsics.
- **D2 — max-range envelope (real imagery, low resolution):** 90.2 cm (outer) recursive tag at 640x480 (Raspberry Pi Camera Module V2) detected from 0.08 to 16.15 +/- 0.03 m. Simple traceable arithmetic: max range ≈ 17.9 tag-widths at 640x480 for this nested layout. Trace: row 3.4. Caveats: nested/recursive layout (outer tag governs max range, inner tags govern min range); Pi V2 intrinsics not stated in text.
- **D3 — falloff-shape statement only (synthetic):** at 400x400 px, f = 400 px, AprilTag 1 "works reliably to 50 m" while ARToolkitPlus drops under 50% around 25 m — but the tag's physical size in this simulation is NOT stated in the text, so this cannot be converted to a size-in-pixels anchor. Use only as qualitative support for a plateau-then-falloff shape. Trace: rows 1.11, 1.13.
- **D4 — small-tag regime:** 4 cm tags at 1296x964 were detectable through part of a 20-160 cm sweep, and the recall difference between detectors "is mostly due to differences in the distance at which the detector begins failing to detect tags" → model recall loss as onset-of-failure distance, not a gradual global degradation. Exact recall-vs-distance values are figure-only. Trace: rows 3.8, 3.10.
- **View-angle dependence: UNANCHORED.** No paper in this corpus states a numeric detection rate or accuracy at any specific off-axis angle in text, tables, or captions (all such data is in Olson Fig. 9, Wang Fig. 6/7, Krogius Fig. 8). The only usable text is directional: performance worsens as the tag normal rotates away from the camera, and Olson's detector maintains detection over a wider angle range than ARToolkitPlus (Sec. VI-B text, re Fig. 9). The angle axis of the injected model must be anchored from MR data — deliberately left without literature shape.

### Pose-covariance class values (PHASE1_PARAMETERS #40)

- **Corner/pixel noise: UNANCHORED by this pass.** The only text statement is qualitative — corner estimates "accurate to a small fraction of a pixel" (row 1.5). The one paper that quantifies corner accuracy in px (Kallwies 2020) is UNAVAILABLE. Do not inject a numeric px sigma from this corpus; take it from MR reprojection residuals.
- **Translation / range error covariance: UNANCHORED.** All range-error magnitudes are figure-only (Olson Fig. 10; Wang Fig. 5, Fig. 9). Not extracted.
- **Rotation error covariance: UNANCHORED.** All orientation-error magnitudes are figure-only (Olson Fig. 9; Wang Fig. 6). Not extracted.

### False-positive / mis-ID class values (well anchored — strongest part of this corpus)

- 36h11, <= 2-bit correction, natural scenes (LabelMe 421,049 images): per-candidate-quad FP rate 0.000044% (AprilTag 2 detector; 6 false detections) vs 0.000284% (old detector; 145); theoretical 0.000570%. Traceable arithmetic: ~1.4e-5 false detections per image (6/421,049) for the new detector. Trace: row 2.5.
- 41h12 (Ising-generated), LabelMe 207,920 images: 0 / 0 / 4 / 44 false positives at 0/1/2/3 bits corrected → ~1.9e-5 per image at 2-bit correction (4/207,920). Trace: row 3.6.
- Circular 21h7 is orders of magnitude worse (85 FPs even at 0-bit correction) — avoid small circular families where FP rate matters. Trace: row 3.7.
- Configuration rule: cap bit-error correction at <= 2 bits ("no known users accept tags with more than two bit errors"). Trace: rows 2.1, 2.4. Theoretical FP growth with correction depth for 36h10/36h15: row 1.6.

---

## Not covered by this corpus (deliberate gaps → MR data)

- **Mud / physical contamination of tags** → MR-001. No fetched paper tests contaminated tags (only partial-occlusion behavior, discussed qualitatively).
- **Calibrated sub-10-lux illumination** → MR-002. No fetched paper reports any lux-calibrated low-light detection numbers.
- **Depth-separated constellation flips / two-solution planar-pose ambiguity** → MR-003. No fetched paper's text, tables, or captions contain ANY numeric data on the two-solution pose ambiguity or flip frequency; the topic is not quantified anywhere in this corpus.
- **All figure-only quantities skipped in this pass:**
  - Olson 2011: Fig. 6 & 7 (empirical FP curves), Fig. 9 (orientation error + detection rate vs off-axis angle), Fig. 10 (range error + detection rate vs distance).
  - Wang & Olson 2016: Fig. 5 (position error vs distance), Fig. 6 (orientation error vs angle), Fig. 7 (% detected vs distance, simulated), Fig. 9 (estimated vs actual distance, real), Fig. 10 (% detected vs distance, real).
  - Krogius 2019: Fig. 7 (recall vs fps sweep), Fig. 8 (recall vs distance for 4 cm tags).
- **View-angle numeric dependence** (consequence of the above): unanchored; MR data must supply it.
- **Corner-noise magnitude in pixels**: only quantified source (Kallwies 2020) UNAVAILABLE; MR data must supply it.

---

## UNVERIFIED

- **Kallwies, Forkel & Wuensche, ICRA 2020 — UNAVAILABLE (no open PDF).** Attempts on 2026-08-02:
  - https://ieeexplore.ieee.org/document/9197427/ — known paywalled (per task brief; not fetched).
  - https://www.mucar3.de/icra2020-apriltags/ — project page fetched; hosts dataset + code links and example ground-truth PDFs only; no paper PDF.
  - https://www.mucar3.de/icra2020-apriltags/paper.pdf — HTTP 404.
  - https://github.com/UniBwTAS/apriltags_tas — README fetched; cites the paper, links only to ResearchGate "Request PDF"; no numeric results in README.
  - Semantic Scholar Graph API (paper 190a6317ebfbe2c6f29b7684f68a5b5a2104c02c) — isOpenAccess: false, openAccessPdf: none.
  - https://www.unibw.de/tas/news/... (institute news page) — fetched; no PDF link.
  - ResearchGate record 344982809 — "Request PDF" only (no public full text).
  - Web searches for a preprint/author copy (incl. athene-forschung.unibw.de) — none found.
  No values were recorded for this paper; nothing was taken from memory.
- **Discarded intermediate output:** the automated summary returned by the first fetch of Olson 2011 contained numbers not present in the paper (e.g., "0.3 pixels", "587 codewords for 36h11 min-Hamming-11 family", "640x480 camera, 10 cm tags, 1-5 m"). It was discarded; every Olson 2011 value above was re-verified by reading the PDF pages directly. The same direct-page-read verification was applied to Papers 2 and 3.
- **2026-08-04 — ninth dead route:** Kalaitzakis author-copy route checked by the D-031 planning session — publications page carries DOI links only, no PDF.
- **2026-08-04 — reproduction caution (fetched raw via GitHub API, not a digest):** github.com/UniBwTAS/apriltags_tas/issues/4, opened 2021-06-18, still open, 8 comments — an independent user running the authors' published `refineCornerPointsByDirectEdgeOptimization` on the authors' own dataset (image `0019.png`, random.zip) could not reproduce the paper's 0.017 px median corner error; the thread records ≈0.70–0.71 px (~40×). **Not peer-reviewed — recorded as caution only, never a CLAIMS source.**
- **2026-08-04 — abstract semantics:** the paper's 0.017 px is the authors' improved edge-refinement method and 0.17 px is OpenCV cornerSubPix; neither is stock-AprilTag corner σ, so the paper would not have directly anchored #40 even if obtained.
- **2026-08-04 — substitution path:** open-access anchor leads (Adámek 2023 first) are tracked in `research/OA_SUBSTITUTION.md` §2; substitutes enter this file only as new numbered papers after Stage B page-verification.
