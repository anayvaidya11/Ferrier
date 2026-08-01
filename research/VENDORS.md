# Project Sustainment — July 2026 Vendor Selection: Partner Research

Prepared for WyZen (autonomous recovery of disabled UGVs). All facts below carry an inline
source URL and retrieval date. Lines labeled **Assessment:** are WyZen analyst opinion, not
sourced fact. Retrieval date for all sources: **2026-07-31**.

## Selection: CONFIRMED from fetched sources

The five-vendor selection is confirmed. The U.S. Army's Capability Program Executive (CPE)
Mission Autonomy selected **AM General, American Rheinmetall, Carnegie Robotics, HDT Robotics
(BLADE), and Stratom** to develop prototypes under Project Sustainment, the Army's effort to
develop and field a medium-sized ground robot for tactical logistics
(Inside Defense, https://insidedefense.com/insider/army-settles-five-companies-sustainment-robot-competition, retrieved 2026-07-31;
The Defense Post, https://thedefensepost.com/2026/07/27/us-army-autonomous-platforms/, retrieved 2026-07-31;
Defense Daily, https://www.defensedaily.com/army-picks-companies-for-new-autonomous-logistics-breaching-prototyping-efforts/army/, retrieved 2026-07-31).

Program facts (all retrieved 2026-07-31):

- Selection announced Friday, July 10, 2026, per Defense Daily's account of the Army
  acquisition office announcement
  (https://www.defensedaily.com/army-picks-companies-for-new-autonomous-logistics-breaching-prototyping-efforts/army/).
  The Defense Post reports the selection was disclosed via LinkedIn
  (https://thedefensepost.com/2026/07/27/us-army-autonomous-platforms/).
- Run through the National Advanced Mobility Consortium (NAMC); requests for prototype
  proposals were issued in April [2026] through NAMC, and awards were still being finalized
  at time of Inside Defense's reporting
  (https://insidedefense.com/insider/army-settles-five-companies-sustainment-robot-competition).
- Program office: CPE Mission Autonomy, recently realigned from PAE Maneuver Air to PAE
  Layered Protection and Integration
  (https://insidedefense.com/insider/army-settles-five-companies-sustainment-robot-competition).
- Goal: "remove soldiers from high-risk delivery routes while delivering essential supplies
  directly to the tactical edge"; field testing with operational units planned for early 2027,
  with a transforming-in-contact rotation focused on the mission in Q2 FY2027
  (https://insidedefense.com/insider/army-settles-five-companies-sustainment-robot-competition;
  https://thedefensepost.com/2026/07/27/us-army-autonomous-platforms/).
- Lineage: builds on the S-MET robotic mule and absorbed the Medium Multipurpose Equipment
  Transport (M-MET) program, per an AM General vice president quoted by Inside Defense
  (https://insidedefense.com/insider/army-settles-five-companies-sustainment-robot-competition;
  https://thedefensepost.com/2026/07/27/us-army-autonomous-platforms/).
- Size class: described only as a "medium-sized ground robot"; no weight/payload class for the
  program has been published in any source fetched
  (https://insidedefense.com/insider/army-settles-five-companies-sustainment-robot-competition).

---

## 1. AM General

- **Platform:** An all-new logistics UGV debuted at AUSA Global Force (March 24–26, 2026,
  Huntsville, AL), built on next-generation light tactical vehicle technology with a
  turbocharged 6.5L 8-cylinder engine (250 hp, 550+ lb-ft, fuel-flexible), a reconfigurable
  cargo deck, a wireless remote-controlled T-boom service crane, and an L-track modular cargo
  fastening system; it also carries Carnegie Robotics' FireAnt sUGV for extended situational
  awareness
  (https://www.amgeneral.com/am-general-is-driving-innovation-at-ausa-global-force-2026-with-unmanned-ground-vehicle-debut/, retrieved 2026-07-31).
  The team's earlier (Oct 14, 2025) M-MET-oriented announcement describes a HUMVEE-chassis
  base with modernized powertrain and suspension, drive-by-wire, MOSA-compliant architecture,
  and a hybrid-electric powerpack delivering over 30 kW of exportable power
  (https://www.amgeneral.com/am-general-announces-collaboration-with-carnegie-robotics-and-textron-systems-to-develop-modular-unmanned-ground-vehicle-for-u-s-army-modernization/, retrieved 2026-07-31).
- **Size class:** Not published. HUMVEE-chassis-derived per the Oct 2025 release (URL above);
  no curb weight or payload figure disclosed in any fetched source.
- **Autonomy partner/stack:** Carnegie Robotics provides the autonomy software stack, sensor
  fusion, compute architecture, and non-weapons payload integration; Textron Systems provides
  drive-by-wire, diagnostics, and the hardware/software control layer for autonomous
  execution; AM General is prime integrator
  (https://www.amgeneral.com/am-general-announces-collaboration-with-carnegie-robotics-and-textron-systems-to-develop-modular-unmanned-ground-vehicle-for-u-s-army-modernization/;
  https://www.amgeneral.com/am-general-is-driving-innovation-at-ausa-global-force-2026-with-unmanned-ground-vehicle-debut/, both retrieved 2026-07-31).
- **Role/status:** One of the five selected prototype developers; an AM General VP told Inside
  Defense that Project Sustainment absorbed the prior M-MET effort
  (https://insidedefense.com/insider/army-settles-five-companies-sustainment-robot-competition, retrieved 2026-07-31).
  Note: no AM General press release specific to the Project Sustainment award was found (see
  UNVERIFIED).
- **Assessment:** A multi-ton HUMVEE-derived UGV that dies on a contested resupply route is a
  mission-stopping recovery problem the Army currently solves with crewed wreckers, so AM
  General has a strong incentive to bolt on autonomous recovery to protect its
  "keeps-the-route-open" value proposition — though WyZen would need to integrate through, or
  around, Carnegie Robotics' incumbent autonomy stack.

## 2. American Rheinmetall

- **Platform:** Hybrid-powered autonomous UGVs (no platform name published) built on partner
  Harbinger's dual-use commercial hybrid chassis, designed to support company-sized element
  sustainment missions by autonomously transporting supplies to and from the forward line of
  troops
  (https://www.prnewswire.com/news-releases/american-rheinmetall-awarded-us-army-contract-for-project-sustainment-to-advance-autonomous-logistics-capabilities-progressing-new-partnership-with-harbinger-302840105.html;
  https://www.rheinmetall.com/en/media/news-watch/news/2026/07/2026-07-31-american-rheinmetall-awarded-us-army-contract-for-project-sustainment, both retrieved 2026-07-31).
- **Size class:** Not disclosed in either release (URLs above) or in trade coverage
  (https://defence-industry.eu/american-rheinmetall-wins-u-s-army-contract-to-develop-hybrid-autonomous-logistics-vehicles-for-contested-battlefield-supply-missions/, retrieved 2026-07-31).
- **Autonomy partner/stack:** Forterra provides the autonomous capabilities; Primordial Labs
  contributes its Anura natural-language human-machine interface; Harbinger provides the
  vehicle/chassis technology; American Rheinmetall is prime
  (https://www.prnewswire.com/news-releases/american-rheinmetall-awarded-us-army-contract-for-project-sustainment-to-advance-autonomous-logistics-capabilities-progressing-new-partnership-with-harbinger-302840105.html, retrieved 2026-07-31).
- **Role/status:** Awarded an 18-month contract (with potential follow-on orders) for Project
  Sustainment, executed through NAMC, as prime contractor; announced July 31, 2026
  (https://www.prnewswire.com/news-releases/american-rheinmetall-awarded-us-army-contract-for-project-sustainment-to-advance-autonomous-logistics-capabilities-progressing-new-partnership-with-harbinger-302840105.html;
  https://www.rheinmetall.com/en/media/news-watch/news/2026/07/2026-07-31-american-rheinmetall-awarded-us-army-contract-for-project-sustainment, both retrieved 2026-07-31).
- **Assessment:** A first-of-type commercial EV-hybrid chassis (Harbinger) entering
  contested-environment field trials carries elevated immobilization risk from powertrain,
  battery, and software faults, making autonomous recovery an attractive de-risking feature —
  but Forterra's incumbency means WyZen's pitch must be a complementary recovery capability,
  not a competing autonomy stack.

## 3. Carnegie Robotics

- **Platform:** No standalone Carnegie Robotics vehicle for Project Sustainment is described
  in any fetched source; trade coverage lists the company among the five selectees but
  describes no independent offering (The Defense Post explicitly provides no standalone
  platform for Carnegie, noting it instead as a partner on BLADE's Dire WOLF:
  https://thedefensepost.com/2026/07/27/us-army-autonomous-platforms/, retrieved 2026-07-31).
  See UNVERIFIED.
- **Size class:** Not applicable / not published — Carnegie is primarily an autonomy and
  sensing software house (autonomy stack, sensor fusion, compute architecture per
  https://www.amgeneral.com/am-general-announces-collaboration-with-carnegie-robotics-and-textron-systems-to-develop-modular-unmanned-ground-vehicle-for-u-s-army-modernization/, retrieved 2026-07-31).
- **Autonomy partner/stack:** Carnegie IS the autonomy provider on at least one other
  selectee's team (AM General — autonomy software stack, sensor fusion, compute, payload
  integration, software sustainment; URL above) and is a named partner in BLADE's award
  release: "We're excited to partner with the Army, NAMC, Michelin and Carnegie Robotics on
  this critical program"
  (https://soldiersystems.net/2026/07/24/blade-awarded-us-army-project-sustainment-contract-for-advanced-autonomous-logistics/, retrieved 2026-07-31).
  Note: BLADE's release does not explicitly state Carnegie's role is autonomy software.
- **Role/status:** Named as one of the five selected companies by Inside Defense
  (https://insidedefense.com/insider/army-settles-five-companies-sustainment-robot-competition),
  Defense Daily
  (https://www.defensedaily.com/army-picks-companies-for-new-autonomous-logistics-breaching-prototyping-efforts/army/),
  and The Defense Post (https://thedefensepost.com/2026/07/27/us-army-autonomous-platforms/),
  all retrieved 2026-07-31. Prior sustainment-autonomy work includes the Army/DIU GEARS
  project (per Carnegie's own news page,
  https://www.carnegierobotics.com/news, retrieved 2026-07-31).
- **Assessment:** As the autonomy supplier threaded through multiple Project Sustainment
  teams, Carnegie is simultaneously WyZen's highest-leverage integration channel and its most
  likely build-it-in-house competitor for recovery behaviors — engage early, because whoever
  owns the autonomy stack decides whether recovery is a bought feature or a native one.

## 4. HDT (BLADE)

- **Platform:** The **Dire WOLF**, a rugged six-wheeled diesel-electric hybrid UGV derived
  from BLADE's WOLF-X robotic combat vehicle, with pivot steering for confined terrain,
  non-pneumatic Michelin Tweels, and exportable onboard battery power; BLADE is the rebranded
  identity of HDT Global
  (https://www.hdtglobal.com/2026/07/23/blade-awarded-u-s-army-project-sustainment-contract-for-advanced-autonomous-logistics/;
  https://soldiersystems.net/2026/07/24/blade-awarded-us-army-project-sustainment-contract-for-advanced-autonomous-logistics/;
  https://www.militaryaerospace.com/uncrewed/article/55393527/blade-unveils-dire-wolf-logistics-ugv-for-the-armys-project-sustainment, all retrieved 2026-07-31).
- **Size class:** Exact weight/payload not published; capable of "transporting thousands of
  pounds of mission-essential cargo," and can negotiate steep slopes, wide gaps, and two-foot
  vertical steps
  (https://soldiersystems.net/2026/07/24/blade-awarded-us-army-project-sustainment-contract-for-advanced-autonomous-logistics/;
  https://thedefensepost.com/2026/07/27/us-army-autonomous-platforms/, both retrieved 2026-07-31).
- **Autonomy partner/stack:** Not explicitly identified. BLADE's release names Michelin and
  Carnegie Robotics as program partners (exact quote in the Carnegie section above), but does
  not state which partner supplies autonomy software
  (https://soldiersystems.net/2026/07/24/blade-awarded-us-army-project-sustainment-contract-for-advanced-autonomous-logistics/, retrieved 2026-07-31).
  Military Aerospace likewise notes autonomy software providers were not disclosed
  (https://www.militaryaerospace.com/uncrewed/article/55393527/blade-unveils-dire-wolf-logistics-ugv-for-the-armys-project-sustainment, retrieved 2026-07-31).
- **Role/status:** Selected as one of five industry partners under NAMC; announcement
  published July 23, 2026, with statement from Tom Van Doren, President of Robotics; no
  contract value or duration disclosed
  (https://www.hdtglobal.com/2026/07/23/blade-awarded-u-s-army-project-sustainment-contract-for-advanced-autonomous-logistics/;
  https://soldiersystems.net/2026/07/24/blade-awarded-us-army-project-sustainment-contract-for-advanced-autonomous-logistics/, both retrieved 2026-07-31).
- **Assessment:** BLADE already markets reliability hardware (Tweels, hybrid redundancy) as a
  differentiator, and autonomous recovery is the logical software completion of that pitch —
  a second Dire WOLF that can retrieve a disabled one forward of the line of troops directly
  extends their "reduce risk to the warfighter" message, making them a natural first
  partnership target.

## 5. Stratom

- **Platform:** No Stratom Project Sustainment platform or offering is described in any
  fetched source (see UNVERIFIED). Company background: Boulder, Colorado-based
  Service-Disabled Veteran Owned Small Business specializing in UGVs and robotic systems,
  with defense logistics programs including the USMC Autonomous Pallet Loader and the
  eXpeditionary Cargo Loader, and its modular "Summit" off-road autonomy software platform
  (Summit Core / Behaviors / Services, launched April 2022)
  (https://www.auvsi.org/news/stratom-launches-summit-off-road-autonomy-platform-to-fast-track-autonomous-systems-in-complex-terrain-environments/;
  https://www.globenewswire.com/search/organization/Stratom, both retrieved 2026-07-31).
  Note: Summit's connection to Project Sustainment is NOT confirmed — background only.
- **Size class:** Not published for any Project Sustainment offering.
- **Autonomy partner/stack:** Not published. Stratom develops its own autonomy software
  (Summit; AUVSI URL above), so it plausibly self-supplies, but no source confirms this for
  Project Sustainment.
- **Role/status:** Named as one of the five selected companies by Inside Defense
  (https://insidedefense.com/insider/army-settles-five-companies-sustainment-robot-competition),
  Defense Daily
  (https://www.defensedaily.com/army-picks-companies-for-new-autonomous-logistics-breaching-prototyping-efforts/army/),
  and The Defense Post (https://thedefensepost.com/2026/07/27/us-army-autonomous-platforms/),
  all retrieved 2026-07-31. Stratom has issued no press release on the selection as of
  2026-07-31 (GlobeNewswire organization page shows nothing after May 11, 2026:
  https://www.globenewswire.com/search/organization/Stratom, retrieved 2026-07-31).
- **Assessment:** As the smallest selectee and a modular-autonomy-software specialist,
  Stratom could productize recovery as simply another "Summit Behavior" module — which makes
  them either the easiest technical integration partner for WyZen or the vendor most tempted
  to write a lightweight recovery behavior themselves.

---

## UNVERIFIED — requires human retrieval

### Program-wide
- **Weight/payload class for Project Sustainment.** No fetched source publishes a class;
  Inside Defense says only "medium-sized ground robot." Tried: Inside Defense, Defense Daily
  (both partially paywalled), The Defense Post, vendor releases. Full text of the paywalled
  Inside Defense and Defense Daily articles may contain figures.
- **Contract values and prototype quantities** for all five awards. Only American
  Rheinmetall's 18-month duration is public. Defense Daily's full (subscriber) article and
  NAMC may hold more.
- **NAMC's own announcement.** namconsortium.org returned HTTP 403 to automated fetch on
  2026-07-31; the consortium's Project Sustainment page/news item could not be retrieved.

### AM General
- **Whether the exact AUSA Global Force 2026 UGV configuration is the Project Sustainment
  offering**, and whether the Textron/Carnegie teaming carries over unchanged to the awarded
  contract. AM General published no Project Sustainment award release found via search or on
  amgeneral.com as of 2026-07-31; the M-MET-to-Project-Sustainment absorption (Inside
  Defense) makes carryover likely but it is not confirmed.

### Carnegie Robotics
- **Carnegie's standalone Project Sustainment offering** (own platform vs. software-only
  award vs. partner-supplied vehicle). Tried: carnegierobotics.com/news (fetched — no Project
  Sustainment item posted), The Defense Post, Inside Defense, Defense Daily. No source
  describes what Carnegie itself is delivering under its own selection.
- **Carnegie's precise role on BLADE's Dire WOLF team** (named as partner; autonomy-software
  role not explicitly stated in BLADE's release).

### HDT/BLADE
- **Dire WOLF exact weight, payload capacity, and dimensions** — only "thousands of pounds"
  published. Tried: hdtglobal.com release, Soldier Systems, Military Aerospace, The Defense
  Post. An hdtglobal.com Dire WOLF product page may exist but was not located via search.
- **Dire WOLF autonomy software provider** — not disclosed in any fetched source.

### Stratom
- **Stratom's Project Sustainment platform, teaming, and autonomy arrangement.** Tried:
  stratom.com/news (HTTP 403 on 2026-07-31), GlobeNewswire Stratom organization page (no
  release after May 11, 2026), web searches combining Stratom with "Project Sustainment."
  Nothing published as of 2026-07-31.
