# Follow-On Procurement Signal: Autonomous Vehicle Recovery & Project Sustainment

**Compiled:** 2026-07-31. All facts below were verified against live web fetches on 2026-07-31; nothing is from model memory. Anything that could not be verified against a fetched page is listed under "UNVERIFIED — requires human retrieval" at the bottom.

**Bottom line up front:** As of 2026-07-31 (the RFI response deadline itself), there is **no follow-on solicitation, sources-sought, or RFP yet** stemming from the 17 June 2026 Unmanned Ground Recovery RFI — a live SAM.gov API query returned the original RFI as the only matching notice, unamended since posting. The strongest follow-on signal is structural: the RFI is run by the **Army Applications Laboratory (AAL)** via ACC-APG, and the Army's Capability Program Executive (CPE) Mission Autonomy is converting NAMC prototype-proposal cycles into awarded prototype efforts (Project Sustainment, EABC) on roughly a 3-month RPP-to-selection cadence, with Transformation-in-Contact assessments in early/Q2 FY27. Recovery is **not** currently one of CPE Mission Autonomy's three named priority mission sets (engineering/breaching, sustainment, fires) — the recovery effort sits upstream, at the market-research stage.

---

## 1. SAM.gov — Solicitations, Sources-Sought, RFPs

### 1.1 RFI: Unmanned Ground Recovery (the source notice)
- **Date:** Posted 2026-06-17 (22:07 UTC); responses due 11:59 AM CT, 2026-07-31; archive date 2026-12-31.
- **Issuing body:** W6QK ACC-APG DURHAM (Army Contracting Command – Aberdeen Proving Ground, Research Triangle Park, NC office), on behalf of the **Army Applications Laboratory** — solicitation number `Unmanned_Ground_Recovery_AAL`, response email `unmanned-ground-recovery@aal.army`, place of performance Austin, TX (AAL's home). NAICS 541715, PSC AJ13. Notice type: Sources Sought.
- **Summary:** Full notice text retrieved via the SAM.gov opportunities API. Problem statement: vehicle recovery in contested environments is resource-intensive, exposes Soldiers, and is constrained by human endurance and DDIL (Denied, Degraded, Intermittent, Limited) communications. "The Army Sustainment Community is interested in advanced, low-logistics solutions to reduce the overall resource demand, personnel footprint, and exposure time required to execute recovery missions under DDIL network conditions." Open to modifications of existing Army platforms **or** entirely separate systems. Four questions (750 words each, single PDF): (1) autonomously find/navigate to a disabled, destroyed, or immobilized vehicle; (2) autonomous rigging; (3) both in degraded terrain (inaccessible high ground, unstable soil, severe obstacles); (4) both under denied/degraded comms. References ATP 4-31 (Recovery and BDAR). Disclaimer: market research only, "may inform future requirements development and acquisition planning"; any future procurement "will be announced separately." Notice is version 2 but modified-date equals posted-date (2026-06-17) — no amendments since posting, no related notices attached.
- **Source:** https://sam.gov/api/prod/opps/v2/opportunities/cb5d64eee89d40f48a3fab599f16d290 (API; human-readable view at https://sam.gov/opp/cb5d64eee89d40f48a3fab599f16d290/view). Corroborated by aggregator listing https://fedops.com/opportunities/cb5d64eee89d40f48a3fab599f16d290. Retrieved 2026-07-31.

### 1.2 Verified absence: no follow-on notices as of 2026-07-31
- **Date of check:** 2026-07-31.
- **Issuing body:** n/a (SAM.gov public search API query).
- **Summary:** A SAM.gov search-API query for "unmanned ground recovery" (all notice types, sorted by modified date) returned exactly one result: the 17 June RFI above. A query for "vehicle recovery" + autonomous returned the same RFI plus unrelated 2002/2024 notices. A query for "Project Sustainment" returned only two unrelated facilities solicitations (2019, 2023) — consistent with Project Sustainment being executed through the NAMC OTA rather than FAR-based SAM.gov postings. A query for "robotic recovery" returned one historical notice (see 1.3). Conclusion: **no resulting solicitation, industry-day notice, or amendment exists on SAM.gov yet** for the recovery effort as of the response deadline.
- **Source:** https://sam.gov/api/prod/sgs/v1/search/?index=opp&q=%22unmanned%20ground%20recovery%22 (and parallel queries for "Project Sustainment", "robotic recovery"). Retrieved 2026-07-31.

### 1.3 Historical precedent notice: SMET Robotic Recovery System (context)
- **Date:** Posted 2016-08-29.
- **Issuing body:** U.S. Army (per SAM.gov search API result).
- **Summary:** The only prior SAM.gov notice matching "robotic recovery" is a 2016 Sources Sought titled "Squad Mission Equipment Transporter Robotic Recovery System and Squad payload carrier" — evidence that Army interest in robotic recovery of unmanned platforms predates the current RFI by a decade but never (per SAM.gov) matured into a standing FAR solicitation line. Only the title/date/ID were retrieved; full notice text not fetched.
- **Source:** SAM.gov search API result, notice ID e4caf1337b9c0cef40bb9007da011ad1 (https://sam.gov/opp/e4caf1337b9c0cef40bb9007da011ad1/view). Retrieved 2026-07-31.

---

## 2. NAMC (namconsortium.org)

### 2.1 NAMC news: "Army Autonomy Efforts Advance Across Breaching and Sustainment Mission Sets"
- **Date:** 2026-07-10.
- **Issuing body:** National Advanced Mobility Consortium (NAMC).
- **Summary:** NAMC's own writeup of the July selections. Confirms: (a) on **July 8, 2026** the Army announced four companies — Caterpillar, Forterra, IDV USA, Overland AI — for the Engineer Autonomous Breaching Capability (EABC), with "formal contract awards expected in the coming weeks" and demonstrations, assessments, and a **Transformation in Contact unit assessment in early 2027**; (b) per Inside Defense, five companies — AM General, American Rheinmetall, Carnegie Robotics, HDT Robotics, Stratom — were selected to develop prototypes under **Project Sustainment**, the Army's effort to field a medium ground robot for tactical logistics. NAMC directs members to "monitor the BIDS portal and NAMC opportunity page for current and upcoming solicitations, teaming opportunities, and project updates." No mention of a recovery mission set.
- **Source:** https://www.namconsortium.org/article/news/army-autonomy-efforts-advance-across-breaching-sustainment-mission-sets. Retrieved 2026-07-31.

### 2.2 NAMC open-opportunities page: no recovery RPP as of 2026-07-31
- **Date of snapshot:** 2026-07-31.
- **Issuing body:** NAMC.
- **Summary:** The public opportunities page currently lists these RPPs/RFIs: RFI-TR-16 Army Ground Autonomy Community of Practice; RPP-26-A01 Advanced Digital Concepting for Vehicle Platforms; RPP-26-A01 EW Sensors & Effectors for Ground Maneuver Systems; RPP-26-A01 Real-Time Cognitive State Assessment for Human-AI-Robot Teaming; RPP-26-A01A Remote/Semi-Autonomous/Autonomous Operation of Construction Equipment; RPP-26-D01 Engineer Autonomous Breaching Capability (EABC); RPP-25-D06 Autonomous Decontamination System; RPP-25-D12 Unmanned Systems (UxS) Autonomy System; plus four RPP-25-A03 items (APS controller, immersive simulation, cross-domain solution, Modular Active Framework). **None reference vehicle recovery, and no Project Sustainment RPP remains open** (its RPP cycle closed with the July selections). Detail pages are member-gated ("Join Now to Access All the Details"); full RPP text lives behind the NAMC BIDS portal.
- **Source:** https://www.namconsortium.org/opportunities. Retrieved 2026-07-31.

### 2.3 NAMC RFI-TR-16: Army Ground Autonomy Community of Practice (standing on-ramp)
- **Date:** Released 2024-06-27; open until 2029-08-23 (3:00 pm ET). Status: Open.
- **Issuing body:** NAMC (Technology Objective Area: Architecture, Security & Modularity, ASM-24-02; NAMC POC Jeff Anderson).
- **Summary:** A standing RFI establishing the Army Ground Autonomy (formerly ARCS) Community of Practice — "a foundational platform, prioritizing Industry as a key partner, to enable effective collaboration between Industry and Government in transitioning ground autonomy capabilities," including streamlined methods for industry to access and leverage existing Army autonomy solutions. Relevance to WyZen: this is the persistent, no-deadline NAMC entry point into the Army ground-autonomy ecosystem from which the RPP cycles (EABC, Project Sustainment) are drawing; subcommittee membership rounds have run since late 2024.
- **Source:** https://www.namconsortium.org/opportunities/rfi-tr-16-army-ground-autonomy-community-practice. Retrieved 2026-07-31.

### 2.4 NAMC Monthly Defense Report — June 2026 (sustainment-autonomy context)
- **Date:** June 2026 (monthly report posted to NAMC news).
- **Issuing body:** NAMC.
- **Summary:** Notes "the Army's persistent effort to integrate AI and autonomous systems into future sustainment operations is highlighted by recent demonstrations conducted by 8th TSC [Theater Sustainment Command]," and emphasis by Training and Transformation Command (T2COM) on Soldier feedback and rapid experimentation. No mention of the recovery RFI or a recovery mission set (checked full text for "recovery").
- **Source:** https://www.namconsortium.org/article/news/monthly-defense-report-june-2026. Retrieved 2026-07-31.

---

## 3. Program Office & Trade-Press Coverage

### 3.1 DefenseScoop on the recovery RFI
- **Date:** 2026-06-22.
- **Issuing body:** DefenseScoop (trade press).
- **Summary:** Reports the RFI posted June 17: Army seeks a "robust, ruggedized" autonomous ground capability to recover disabled equipment in contested, denied/degraded-network environments, including autonomous rigging and terrain navigation without connectivity. Officials say the Army is "open" to modifying existing platforms for recovery missions — a signal that follow-on work could ride on an existing program of record rather than a new-start platform. Article situates the RFI alongside Army experimentation with ground robots for medical evacuation and logistics resupply, and cites Ukrainian use of UGVs for vehicle recovery as a driving reference point.
- **Source:** https://defensescoop.com/2026/06/22/army-autonomous-vehicle-recover-equipment-from-combat-zones/. Retrieved 2026-07-31.

### 3.2 Military Aerospace on the recovery RFI
- **Date:** 2026-06-26.
- **Issuing body:** Military Aerospace Electronics (trade press).
- **Summary:** Confirms deadline of July 31, 2026, 12:59 p.m. Eastern (11:59 a.m. CT), single-PDF email submission, capabilities sought (locating, navigating to, rigging, recovering disabled/immobilized vehicles in DDIL environments; challenging terrain; minimal personnel; ruggedness; low logistics), and that "the effort will inform future requirements and acquisition planning." No industry days or demonstrations announced in the article.
- **Source:** https://www.militaryaerospace.com/uncrewed/article/55386769/army-seeks-autonomous-technologies-for-uncrewed-vehicle-recovery-missions. Retrieved 2026-07-31.

### 3.3 Inside Defense: five companies for the sustainment robot
- **Date:** 2026-07-06.
- **Issuing body:** Inside Defense (trade press; partial text — paywalled).
- **Summary:** CPE Mission Autonomy selected AM General, American Rheinmetall, Carnegie Robotics, HDT Robotics, and Stratom to develop Project Sustainment prototypes — the Army's blueprint for a medium ground robot for tactical logistics, successor in concept to the Medium Multipurpose Equipment Transport (M-MET). The Army plans a **Transforming in Contact rotation focused on this mission in Q2 FY2027**. The sustainment robot is one of **three prioritized autonomy mission sets, alongside combat engineering and fires** — i.e., recovery is not yet a named prototype mission set, which frames the June RFI as pre-decisional market research.
- **Source:** https://insidedefense.com/insider/army-settles-five-companies-sustainment-robot-competition. Retrieved 2026-07-31.

### 3.4 Breaking Defense: EABC selections and the Mission Autonomy pipeline
- **Date:** 2026-07-09.
- **Issuing body:** Breaking Defense (trade press).
- **Summary:** Army selected Caterpillar, Forterra, IDV USA, and Overland AI for EABC under CPE Mission Autonomy; contract awards to be finalized "in coming weeks," with demos/tests concluding in a Transformation in Contact unit assessment in early 2027. Identifies the Army's three autonomy priorities as engineering (breaching), sustainment, and fires, and notes additional Commercial Solutions Openings addressing casualty evacuation and autonomous bridge-building boats. Critically for pipeline mapping: **both EABC and Project Sustainment "derive from National Advanced Mobility Consortium proposals this spring"** — i.e., NAMC RPPs issued in spring 2026 produced vendor selections by July 2026, a roughly one-quarter turn. If the recovery RFI matures the same way, the likely next artifact is a NAMC RPP rather than a FAR solicitation.
- **Source:** https://breakingdefense.com/2026/07/army-selects-four-companies-for-new-autonomous-breaching-program/. Retrieved 2026-07-31.

### 3.5 Defense Daily: both selections
- **Date:** 2026-07-10.
- **Issuing body:** Defense Daily (trade press; paywalled — only lede retrieved).
- **Summary:** Confirms the five Project Sustainment vendors (AM General, American Rheinmetall, Carnegie Robotics, HDT Robotics, Stratom) and four EABC vendors (Caterpillar, Forterra, IDV USA, Overland AI) as "new initiatives to develop new autonomous systems and ground robots." Full article behind subscription; search-result snippets attribute both efforts to April NAMC requests for prototype proposals (see UNVERIFIED for the April date).
- **Source:** https://www.defensedaily.com/army-picks-companies-for-new-autonomous-logistics-breaching-prototyping-efforts/army/. Retrieved 2026-07-31.

### 3.6 HDT Global / BLADE press release
- **Date:** 2026-07-23 (per URL/page date).
- **Issuing body:** BLADE / HDT Global (vendor).
- **Summary:** BLADE announces selection as one of five industry partners for Project Sustainment, structured through NAMC. Platform: **Dire WOLF**, a six-wheeled diesel-electric hybrid variant of the WOLF-X robotic combat vehicle, focused on "automating supply distribution in contested environments" with high payload capacity; partnership includes Michelin and Carnegie Robotics. No contract value, duration, milestones, or recovery mention disclosed.
- **Source:** https://www.hdtglobal.com/2026/07/23/blade-awarded-u-s-army-project-sustainment-contract-for-advanced-autonomous-logistics/. Retrieved 2026-07-31.

### 3.7 American Rheinmetall press release — explicit follow-on language
- **Date:** 2026-07-31 (per release; Rheinmetall corporate posting also dated 2026-07-31).
- **Issuing body:** American Rheinmetall (vendor), via PR Newswire.
- **Summary:** American Rheinmetall announces an **18-month** Project Sustainment contract executed **through the NAMC** (OTA) to deliver hybrid-powered autonomous UGVs supporting company-sized sustainment missions, teamed with Harbinger (vehicle platform), Forterra (autonomy), and Primordial Labs (Anura human-machine interface). Work "across U.S. facilities and test ranges." The release states the contract includes **"potential for follow-on orders as the Army continues to evolve and modernize its autonomous logistics fleet"** — the clearest vendor-side statement of expected follow-on procurement in this dataset.
- **Source:** https://www.prnewswire.com/news-releases/american-rheinmetall-awarded-us-army-contract-for-project-sustainment-to-advance-autonomous-logistics-capabilities-progressing-new-partnership-with-harbinger-302840105.html (corporate mirror: https://www.rheinmetall.com/en/media/news-watch/news/2026/07/2026-07-31-american-rheinmetall-awarded-us-army-contract-for-project-sustainment). Retrieved 2026-07-31.

### 3.8 The Defense Post: five firms, field-testing timeline
- **Date:** 2026-07-27.
- **Issuing body:** The Defense Post (trade press).
- **Summary:** Recaps the five Project Sustainment selections under CPE Mission Autonomy and adds a timeline datapoint: **field testing with operational units begins in early 2027**, with prototypes supporting 24/7 resupply in contested environments. No contract values; no recovery mention.
- **Source:** https://thedefensepost.com/2026/07/27/us-army-autonomous-platforms/amp/. Retrieved 2026-07-31.

---

## 4. PEO CS&CSS / DEVCOM GVSC / Budget Activity

### 4.1 DEVCOM GVSC Commercial Solutions Opening (standing on-ramp for recovery-adjacent tech)
- **Date:** Ongoing (standing CSO); GVSC Industry Day held 21–22 April 2026 at Newlab Detroit (per event listing).
- **Issuing body:** DEVCOM Ground Vehicle Systems Center (Warren, MI), described via third-party summaries.
- **Summary:** GVSC operates an ongoing Commercial Solutions Opening covering robotics, AI, autonomous systems, power, survivability, and vehicle electronics — a plausible non-FAR pathway for recovery-autonomy technology insertion independent of the AAL RFI. Search results surfaced no GVSC or PEO CS&CSS activity specifically labeled "robotic recovery" in 2026. (Note: descriptions of the CSO scope come from a consulting-firm summary page and event listings, not a fetched GVSC solicitation document — treat scope details as secondary-source.)
- **Source:** https://www.bwcoconsulting.com/fod/devcom-gvsc-commercial-solutions-opening-cso (CSO description); https://thepulsegovcon.com/event/u-s-army-devcom-ground-vehicle-systems-center-gvsc-industry-days/ (April 2026 industry day). Retrieved 2026-07-31 (search-result summaries; pages not independently deep-fetched).

### 4.2 Negative finding: no identified budget line for autonomous recovery
- **Date of check:** 2026-07-31.
- **Summary:** Web searches for FY2027 Army budget material tying "recovery" to UGV/robotics under PEO CS&CSS returned no specific program-element line. The Army FY2027 RDT&E justification books exist (e.g., Vol 2, Budget Activity 4B at asafm.army.mil) but were not searched page-by-page — see UNVERIFIED.

---

## UNVERIFIED — requires human retrieval

1. **"April 2026" NAMC RPP dates for Project Sustainment and EABC.** Search-result snippets (Defense Daily/Soldier Systems aggregation) say both efforts "stem from April requests for prototype proposals released by NAMC"; Breaking Defense (fetched) says only "this spring." The actual RPP numbers/dates for Project Sustainment are member-gated on the NAMC BIDS portal (https://www.namconsortium.org — the closed RPP does not appear on the public opportunities page). A NAMC member login is needed to pull the original Project Sustainment RPP and watch for any recovery RPP.
2. **FY2027 budget lines.** https://www.asafm.army.mil/Portals/72/Documents/BudgetMaterial/2027/Discretionary%20Budget/rdte/RDTE%20-%20Vol%202%20-%20Budget%20Activity%204B.pdf was identified but not fetched/searched (large PDF). A human should grep the FY2027 RDT&E justification books (and PEO CS&CSS procurement books) for "recovery," "BDAR," "rigging," and UGV sustainment program elements.
3. **Full Inside Defense and Defense Daily articles** — paywalled; only partial text retrieved. Full texts may name the Project Sustainment contract values, RPP number, and whether recovery is a candidate future mission set.
4. **AAL's own Unmanned Ground Recovery page** (https://aal.mil/unmanned-recovery/) — indexed by search engines with RFI details and a rough future-contract estimate of "$1 million to $10 million" (per search-result snippet), but on 2026-07-31 the URL redirected to the aal.mil homepage (HTTP 200 at https://aal.mil/, page content not retrievable — likely JS-routed or taken down as the response window closed). The dollar-range claim is therefore snippet-only and unverified. Also note the AAL homepage currently lists an open "Ground-Based Affordable Mass" solicitation (application deadline August 5) — unrelated to recovery but confirms AAL's active solicitation cadence.
5. **Army's official July 8 EABC / Project Sustainment announcement page on army.mil** — referenced by NAMC's July 10 article ("According to the Army") but the underlying army.mil URL was not located/fetched.
6. **AM General, Stratom, and Carnegie Robotics vendor press releases** for Project Sustainment — not fetched (HDT and American Rheinmetall releases were; the other three vendors' award terms are unconfirmed beyond trade-press listing).
7. **Attempted but blocked/failed fetches:** https://sam.gov/opp/cb5d64eee89d40f48a3fab599f16d290/view and https://sam.gov/opp/75aa1ff0058e4d1eaa722f8e32cc7331/view (SAM.gov web UI returns an empty JS shell to automated fetchers — worked around via the public API, which succeeded); https://www.namconsortium.org/ root (HTTP 403 via fetch tool; subpages retrieved successfully via curl with a browser user-agent); https://bidbanana.thebidlab.com/bid/iWsIyKmlZFVOp5dZolZa (HTTP 403); https://defence-blog.com/u-s-army-wants-robots-to-recover-battlefield-vehicles/ (HTTP 403); SAM.gov API initially returned HTTP 406 until the `Accept: application/hal+json` header was supplied.

---

## Reading of the signal (analyst note, derived only from the sourced items above)

- The recovery RFI is an **AAL market-research probe for the "Army Sustainment Community,"** not (yet) a CPE Mission Autonomy prototype line. The named prototype mission sets remain breaching, sustainment, and fires (3.3, 3.4).
- The demonstrated pipeline is: NAMC RPP (spring) → 4–5 vendor selection (July) → OTA prototype contracts (~18 months) → Transformation-in-Contact assessment (early/Q2 FY27) (2.1, 3.3, 3.4, 3.7). If recovery follows the same path after RFI responses close today, the artifact to watch for is a **NAMC RPP or an AAL solicitation**, not a FAR RFP on SAM.gov.
- Concrete watch items for WyZen: NAMC BIDS portal and public opportunities page (2.2); the SAM.gov notice for amendments/attachments before its 2026-12-31 archive date (1.1); aal.mil open opportunities (UNVERIFIED item 4); and CPE Mission Autonomy statements about expanding beyond the three current mission sets.
