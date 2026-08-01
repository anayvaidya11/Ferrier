# Army Battery-Interface Standards: MIL-STD-3078 and the STUB Family

**Prepared:** 2026-07-31. All source URLs were retrieved on 2026-07-31 unless noted.
**Purpose:** Establish precisely what existing Army battery-interoperability standards do and do not cover, as groundwork for WyZen's proposed recovery/docking interface for disabled UGVs (field recharging and battery swap).

**Sourcing note:** The full text of MIL-STD-3078 (base issue, 14 Nov 2024, Distribution Statement A) was successfully downloaded from DLA's ASSIST/Quick Search system and read in its entirety; claims about that document are drawn from its actual text. The STUB family's governing performance specification (MIL-PRF-32383/7) could **not** be retrieved; STUB claims rest on MIL-STD-3078's Table I, a 2023 Power Sources Conference technical paper by the STUB manufacturer, and Army/trade press. All statements labeled *inference* are derived from what the fetched sources omit, not from unread document text.

---

## 1. MIL-STD-3078 — Interoperability Standard for Batteries Utilized in Army Equipment

### 1.1 Formal identity and scope

- **Full title:** "Department of Defense Interface Standard — Interoperability Standard for Batteries Utilized in Army Equipment," designated **MIL-STD-3078**, dated **14 November 2024** (base issue; no revision letter). Marked "Not Measurement Sensitive," AMSC N/A, FSG 61GP, Distribution Statement A (approved for public release). Full PDF retrieved via DLA Quick Search: https://quicksearch.dla.mil/WMX/Default.aspx?token=5792701 (retrieved 2026-07-31; the PDF's own footer states "Source: https://assist.dla.mil").
- **Scope (para 1.1, quoted):** "This document provides the interface standard for Army systems utilizing replaceable batteries. It provides information to ensure interoperability of batteries across systems within the Army." (Same source, retrieved 2026-07-31.)
- **Custodian / preparing activity:** Army – CR (CECOM), Project 61GP-2024-001 (concluding material of the standard, same URL, retrieved 2026-07-31).
- **Supersession (para 6.3):** Supersedes the *Preferred Battery List* published by the Power Sources Center of Excellence (PSCOE) (same URL, retrieved 2026-07-31).
- **Maintenance:** The C5ISR Center maintains the standard and can update it "as new standard battery form factors are required," per the Army's battery portal: https://battery.army.mil/system-integrator-hub/mil-std-3078/ (retrieved 2026-07-31).
- **Intended use (para 6.1, quoted):** "This standard is to be used by system developers when selecting a battery for a system under development." (Quick Search URL above, retrieved 2026-07-31.)

### 1.2 What it actually standardizes — mechanical vs electrical

MIL-STD-3078 is a short (11-page + front matter) **selection and pointer standard**, not a dimensioned interface drawing. Its normative core is:

- **General requirement (para 4.1):** "United States Army systems utilizing replaceable batteries **shall** use either military standard batteries (see 5.1) or select COTS batteries (see 5.3)... Preferred military batteries (see 5.2) shall be given precedence." (Quick Search URL above, retrieved 2026-07-31.)
- **Table I — Preferred military batteries** (para 5.2), five configurations recommended for new system design (same source, retrieved 2026-07-31):
  | Configuration | Example nomenclatures | Description (as printed) | Governing spec(s) |
  |---|---|---|---|
  | XX72 | BA-5372# | Low power, cylindrical | MIL-PRF-32271/8 (non-rechargeable) |
  | **STUB** | BB-2511#–BB-2514#, BB-2521#–BB-2524# | "Family of multiple sized batteries sharing same connectors and voltage characteristics. Regulated voltage output." | MIL-PRF-32383/7 (rechargeable) |
  | XX90 | BA-5590#, BA-5390#, BA-5790#, BB-2590# | Rectangular box shaped, dual voltage | MIL-PRF-32271/1; MIL-PRF-32383/3, /5 |
  | Conformal Wearable Battery (CWB) | BB-2525# | Flat, flexible, designed to be Soldier worn | MIL-PRF-32383/4 |
  | 6T | N/A | Box shaped, high power | MIL-PRF-32565; MIL-PRF-32143 |
- **Table II — Approved open-standard COTS batteries** (para 5.3): ANSI C18.3M-defined cells — 'Lithium' AA (ANSI 15LF), 'Lithium' AAA (ANSI 24LF), xx123 (5018LC), xx2032 (5004LC) — with per-item **cell-count limits (4, 4, 4, 2) imposed "for safety reasons."** (Same source, retrieved 2026-07-31.)
- **Mechanical and electrical detail is delegated, not defined.** Para 5.1 states battery details "can be found in published Military Performance Specifications (MIL-PRFs)" and that "System interfaces should be designed to accommodate as many variants as possible." Table II Note 1 states NSNs "should not be considered as a definitive description of the battery interface. Full interface parameters shall be as described in the referenced specifications." Appendix A para 1.1 says outright: "Specific measurements, values, and limits are not discussed here as they vary from battery to battery." (Same source, retrieved 2026-07-31.)
- **Appendix A is explicitly non-mandatory guidance** ("general information, best practices, and lessons learned... should not be viewed as an exhaustive authority"). It covers, descriptively: base specs vs slash sheets; designing to spec tolerances rather than to sample hardware; thermal behavior; electrical definitions (OCV, CCV, cutoff, nominal, regulated output, maximum load, voltage delay); battery compartment venting design (pointing to TB 43-6135); output connectors (noting keying variants, e.g., preventing non-rechargeables from mating with chargers); state-of-charge indicators; complete-discharge devices (TB 43-0134); and 'smart' batteries — where it notes only that "Battery specifications will reference the relevant communication protocols needed to communicate with the battery," i.e., **MIL-STD-3078 itself names no data bus (no SMBus/CAN/USB mandate).** (Same source, retrieved 2026-07-31.)

### 1.3 What MIL-STD-3078 explicitly does NOT cover

Drawn from the fetched full text (Quick Search URL above, retrieved 2026-07-31):

- **Non-replaceable batteries** — para 4.2: batteries "permanently installed in a system and not designed to be replaced are not subject to the requirements of this document" (examples given: reserve battery in an armament; COTS item with embedded rechargeable).
- **Dimensions, voltages, connector geometry, pinouts, data protocols** — all delegated to the referenced MIL-PRF base specifications and slash sheets (paras 5.1, 5.3 Note 1, Appendix A 1.1). The standard contains no dimensioned drawing of any interface.
- **Charging protocols and chargers** — the standard levies no charger-interface or charge-profile requirements. "Availability of charging infrastructure" appears only as a factor acquisition documents *should specify* (para 6.2), and chargers appear in Appendix A only as descriptive guidance. *Inference from the full fetched text:* charger-side interfaces and per-chemistry charge profiles are outside its scope.
- **Aviation** — Table I Note 3: "there is not yet a common standard battery specifically designed for aviation applications. Work is ongoing to develop this standard."
- ***Inference from the full fetched text* — nothing platform-side or robotic:** the document contains no requirements for vehicle-side docking geometry, battery-compartment location or accessibility on a platform, blind-mate or autonomous mating features, alignment/guidance features, tow or recovery interfaces, or robot-to-robot power transfer. Its unit of standardization is the battery an equipment developer selects, not the machinery that would swap or service it.

### 1.4 Adoption signal

- The "shall use" language of para 4.1 makes it binding on Army system developments that invoke it; para 4.1.1 notes "Various policy documents require the use of standard batteries as defined in this document." (Quick Search URL above, retrieved 2026-07-31.)
- The Army stood up battery.army.mil (launched 2024) with a System Integrator Hub and, as of March 2026, an experimental AI-assisted tool for choosing MIL-STD-3078-compliant batteries: https://battery.army.mil/system-integrator-hub/mil-std-3078/ and https://battery.army.mil/new-military-standard-for-batteries/ (both retrieved 2026-07-31).
- An August 2025 Army release (mirrored by Soldier Systems Daily; the army.mil original blocked automated retrieval) describes program managers adopting the standard batteries, with standardized batteries being delivered in GPS devices and radios and research into central power for helmet- and small-arms-mounted systems: https://soldiersystems.net/2025/08/19/army-accelerates-adoption-of-advanced-batteries-through-st-integration/ (retrieved 2026-07-31).
- Joint caveat (Appendix A 2.1.1): Navy/USMC-shared platforms should also consult NAVSEA's preferred-battery lists — MIL-STD-3078 is an Army document usable DoD-wide, not a joint mandate. (Quick Search URL above, retrieved 2026-07-31.)

---

## 2. STUB — Small Tactical Universal Battery family

### 2.1 Formal identity and scope

- **Governing documents:** Within MIL-STD-3078 Table I, STUB is the preferred rechargeable configuration for small/handheld equipment, with example nomenclatures **BB-2511# through BB-2514# and BB-2521# through BB-2524#** (eight nomenclatures; '#' is the generation/modification placeholder per MIL-STD-196), specified by **MIL-PRF-32383/7**, "Battery, Rechargeable, Sealed, Small Tactical Universal Battery (STUB), BB-251X/U and BB-252X/U," a slash sheet under base spec MIL-PRF-32383 (quicksearch.dla.mil WMX URL above, retrieved 2026-07-31; slash-sheet title confirmed via standards catalog listings surfaced in web search — see UNVERIFIED for the spec text itself).
- **Origin:** Program kicked off **July 2020** by DEVCOM C5ISR Center (team led by Dr. Nathan L. Sharpes), with the EXO Charge division of Xentris Wireless as developer, following a C5ISR-commissioned feasibility demonstration of putting USB Power Delivery into military battery-management circuitry. Source: Stein, Whetstone, Patel (Xentris/EXO Charge), "The Small Tactical Universal Battery Series — Helping To Solve Modern Tactical Power Challenges," Power Sources Conference 2023, paper P-4: https://www.powersourcesconference.com/PowerSources23/docs/P-4.pdf (retrieved 2026-07-31).
- **Design intent:** a standard, USB-enabled, centralized power source supporting multiple voltages, per three C5ISR human-factors criteria set in 2018–2019 studies: (1) common interface, (2) constant 2-D cross-section, (3) growth in the third dimension for capacity (same P-4 paper, retrieved 2026-07-31). C5ISR's 2020 standardization road map places STUB in the "handheld" echelon, between an accessory-scale enabler (OSCAR), the soldier-worn CWB, the ruck-able xx90, and the vehicle-scale 6T (P-4 paper, Fig. 4, retrieved 2026-07-31).

### 2.2 Mechanical coverage

- **Eight sizes/capacity options** sharing "the same standard connection interface," offered in single and double cell-stack configurations (P-4 paper, retrieved 2026-07-31). Army C5ISR describes "eight different size options... along with multiple attachment methods — such as slide on, clip in and twist on," with Dr. Sharpes quoted: "Any battery in the STUB family will be able to attach to any device designed for it because of the standard interface": https://soldiersystems.net/2021/09/22/army-modernizes-tactical-power-with-battery-interoperability/ (mirror of Army release of 2021-09-22; retrieved 2026-07-31; the army.mil original returned HTTP 403 to automated retrieval).
- MIL-STD-3078 Table I characterizes the family as "sharing same connectors and voltage characteristics" (Quick Search URL above, retrieved 2026-07-31).

### 2.3 Electrical coverage

Per the manufacturer's Power Sources 2023 paper (P-4 URL above, retrieved 2026-07-31):

- **Chemistry/configuration:** rechargeable lithium-ion packs, 1-cell (1S1P) through 8-cell (4S2P); capacity 3.5 Ah (xS1P) or 7 Ah (xS2P).
- **Interface:** USB Power Delivery (PD) with Programmable Power Supply (PPS) output; terminals are VBus, GND, and CC (communication channel); reversible, bi-directional, multi-voltage power through a **USB-C connector**. The data/negotiation protocol is therefore **USB PD/CC — not SMBus** (in the fetched sources; the unfetched MIL-PRF-32383/7 slash sheet is the authority — see UNVERIFIED).
- **Output voltages:** 5 V, 9 V, 12 V, 15 V, 20 V via PD; 3.3 V and 11 V via 1S1P PPS. Maximum discharge current 750 mA to 5 A depending on voltage and pack configuration. MIL-STD-3078 Table I likewise notes "Regulated voltage output" (Quick Search URL, retrieved 2026-07-31).
- **Charging:** via the USB PD interface — "any USB PD compliant charger can be used to execute fast charging"; packs can also be charged through the VBus/GND contact terminals; adapters for standard Army chargers (ABC and UBC) were "in development" as of the 2023 paper. A "double-tap" gesture shows state of charge on LEDs and enables **STUB-to-STUB power transfer** over a USB-C cable.
- **Certifications (as of 2023):** USB-IF certified; certified to MIL-STD-810H, MIL-STD-461G, UN 38.3, and IP68; MIL-PRF qualification then in progress.

### 2.4 What STUB does NOT cover

- **Scale:** STUB is a handheld/small-form-factor family (radios, GPS, night vision, satcom terminals, sensors, ranging/targeting systems, mine detectors — P-4 paper, retrieved 2026-07-31). Vehicle-scale energy is the 6T's domain (MIL-PRF-32565/32143) in both MIL-STD-3078 Table I and the C5ISR road map. *Inference from fetched sources:* STUB is not sized or specified as a UGV traction/propulsion battery; at 3.5–7 Ah and ≤20 V/≤5 A it could at most power a UGV's payload electronics.
- ***Inference from all fetched sources:*** nothing in the fetched material standardizes the **device-side receptacle envelope beyond battery fit**, robotic/blind-mate insertion features, vehicle docking geometry, high-rate external charge ports, tow/recovery hard points, or autonomous mating. The attachment methods described (slide-on, clip-in, twist-on) are human-hand operations.
- **Charge-profile detail per chemistry** is delegated to USB PD/PPS negotiation and to the MIL-PRF-32383 base spec + /7 slash sheet, not to MIL-STD-3078 (P-4 paper and MIL-STD-3078 text, both retrieved 2026-07-31).

### 2.5 Adoption signal

- **Preferred-battery status:** STUB is one of five preferred configurations that Army developments "shall" draw from under MIL-STD-3078 para 4.1/5.2 (Quick Search URL, retrieved 2026-07-31).
- **Transition to production and fielding:** August 2025 Army reporting (Soldier Systems mirror) states the effort has moved to manufacturing, with standardized batteries being delivered in GPS devices and radios and PMs adopting first-generation STUB into fielded equipment: https://soldiersystems.net/2025/08/19/army-accelerates-adoption-of-advanced-batteries-through-st-integration/ (retrieved 2026-07-31). Trade coverage of the same release lists applications including the M7/M250 (NGSW with XM157 fire control) and counter-UAS equipment: https://www.wearethemighty.com/military-news/the-armys-small-tactical-universal-battery-stub/ (retrieved 2026-07-31).
- Defense News (2024-10-15) reported possible fielding "as early as fiscal 2025," alongside a separate PEO Soldier "battery hub" recharging/power-management effort: https://www.defensenews.com/land/2024/10/15/all-the-high-tech-gear-the-army-is-bringing-to-soldiers/ (retrieved 2026-07-31).
- The NGSW solicitation's requirement for a powered rail with a common weapon-mounted power source is cited by the P-4 paper as an accelerant for the standardized-battery push (P-4 URL, retrieved 2026-07-31).

---

## 3. Implications for WyZen (analysis — labeled inference throughout)

*The following is WyZen analysis derived from the fetched sources above, not a claim from any standard's text.*

1. **The white space is real.** MIL-STD-3078 standardizes *which battery* a developer picks; MIL-PRF slash sheets standardize *the battery itself*. Neither fetched source standardizes the platform-side mechanics of autonomous access: docking geometry, blind-mate tolerance, robotic latch actuation, recovery hard points, or vehicle-to-vehicle power transfer. A WyZen recovery/docking interface would not conflict with either document.
2. **Constraints WyZen should design to anyway:** (a) any swap mechanism handling STUB/CWB/XX90/6T should accommodate full MIL-PRF dimensional tolerances, per MIL-STD-3078 Appendix A 2.3.3's admonition to design to the spec, not to sample hardware; (b) field recharging of STUB-class packs can ride on USB PD/PPS (any compliant source), while 6T-class recharging has no analogous universal external-port standard in the fetched material; (c) MIL-STD-3078 para 4.2 means a UGV's *permanently installed* traction pack sits entirely outside the standard — the exact case a battery-swap architecture would convert into a "replaceable battery," pulling it *into* MIL-STD-3078's scope.
3. **Precedent to cite:** the STUB program shows the Army's accepted pattern for a new interface — C5ISR-led requirements, an industry-built family, then capture as a MIL-PRF slash sheet plus a Table I row in MIL-STD-3078 (which the standard says can be updated "as new standard battery form factors are required" — battery.army.mil page, retrieved 2026-07-31). A recovery/docking interface could plausibly follow the same intake path.

---

## UNVERIFIED — requires human retrieval

- **MIL-PRF-32383/7 (STUB slash sheet) full text — NOT retrieved.** This is the authoritative source for STUB dimensions, connector drawing, pinout, protocol requirements, and charge parameters. Attempts on 2026-07-31: GlobalSpec catalog pages https://standards.globalspec.com/std/14609391/mil-prf-32383-7-1 returned HTTP 403. Web-search catalog listings (GlobalSpec, Document Center, Intertek Inform) indicate a base document (Intertek's listing title says 2022) and at least one revision "(1)", but I did not fetch those pages' contents; treat the 2022 date and revision status as unconfirmed. Retrieve via ASSIST (https://assist.dla.mil, login required) or DLA Quick Search.
- **MIL-PRF-32383 base spec, MIL-PRF-32271 series, MIL-PRF-32565, MIL-PRF-32143, TB 43-6135, TB 43-0134** — referenced by MIL-STD-3078 but not retrieved.
- **army.mil originals blocked (HTTP 403 to automated retrieval on 2026-07-31):** https://www.army.mil/article/247141/... (2021 STUB announcement) and https://www.army.mil/article/287894/... (2025 adoption article). Content was sourced from the Soldier Systems Daily mirrors cited above; a human should spot-check the mirrors against the originals.
- **APG News mirror dead:** https://apgnews.com/inside-the-innovation/army-modernizes-tactical-power-with-battery-interoperability/ returned HTTP 404 on 2026-07-31.
- **battery.army.mil Table I detail:** the MIL-STD-3078 page states some associated technical details are distributed only to .mil email recipients (per the page as fetched 2026-07-31); a human with Army credentials should pull the System Integrator Hub materials and the March-2026 "MIL-STD-3078 AI Agent" tool outputs.
- **Currency check:** the fetched MIL-STD-3078 PDF (14 Nov 2024 base) carries ASSIST's own warning to "check the source to verify that this is the current version before use." Confirm on ASSIST that no revision or change notice has issued since.
- **OSCAR (Operational Single Cell for Accessory Readiness) and the PEO Soldier "battery hub"** — mentioned in fetched sources (P-4 paper Fig. 4; Defense News 2024) but not further sourced; relevant to WyZen's charging story and worth targeted retrieval.
