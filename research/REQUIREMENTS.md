# Requirements Derived from RFI: Unmanned Ground Recovery

Source of record: SAM.gov notice `cb5d64eee89d40f48a3fab599f16d290`, solicitation `Unmanned_Ground_Recovery_AAL`, posted 2026-06-17 by W6QK ACC-APG DURHAM, responses due 2026-07-31 11:59 AM CT.
Primary source URL: `https://sam.gov/api/prod/opps/v2/opportunities/cb5d64eee89d40f48a3fab599f16d290` (raw JSON, retrieved 2026-07-31). Full verbatim text: see `RFI_ACC-APG.md` in this directory.

Question labels Q1–Q4 refer to the four "QUESTIONS FOR CONSIDERATION" in their original list order. In the source they are an unnumbered bulleted list; the Q-numbers are WyZen-assigned reference labels, not Army numbering.

- Q1: "How would you autonomously find and navigate to a disabled, destroyed, or immobilized vehicle?"
- Q2: "How would you conduct an autonomous rigging operation for a disabled, destroyed, or immobilized vehicle?"
- Q3: "How would you accomplish the autonomous navigation and rigging operations in a degraded environment or geographically challenging terrain (i.e. inaccessible high ground, unstable soil, severe obstacles, etc.)"
- Q4: "How would you complete the autonomous navigation and rigging operations in a degraded or denied communication environment?"

Tagging: [DIRECT] = the Army stated it in the RFI text. [INFERRED] = WyZen's reading between the lines of what the Army asked; not stated by the Army.

---

## Capability requirements

### REQ-001 [DIRECT] Autonomous target location
The system shall autonomously find (locate) a disabled, destroyed, or immobilized vehicle.
Source: Q1 — "How would you autonomously find and navigate to a disabled, destroyed, or immobilized vehicle?" (SAM.gov API, retrieved 2026-07-31)

### REQ-002 [DIRECT] Autonomous navigation to target
The system shall autonomously navigate to the disabled, destroyed, or immobilized vehicle.
Source: Q1 (same verbatim question as REQ-001). (SAM.gov API, retrieved 2026-07-31)

### REQ-003 [DIRECT] Autonomous rigging
The system shall conduct an autonomous rigging operation on a disabled, destroyed, or immobilized vehicle.
Source: Q2 — "How would you conduct an autonomous rigging operation for a disabled, destroyed, or immobilized vehicle?" (SAM.gov API, retrieved 2026-07-31)

### REQ-004 [DIRECT] Operation in degraded environments and challenging terrain
The system shall accomplish the autonomous navigation and rigging operations in a degraded environment or geographically challenging terrain, including (Army's own examples) "inaccessible high ground, unstable soil, severe obstacles."
Source: Q3 (verbatim above). (SAM.gov API, retrieved 2026-07-31)

### REQ-005 [DIRECT] Operation under degraded or denied communications (DDIL)
The system shall complete the autonomous navigation and rigging operations in a degraded or denied communication environment. The Problem Statement frames this as DDIL: "network communications being Denied, Degraded, Intermittent, and Limited (DDIL)."
Source: Q4 (verbatim above) and Problem Statement. (SAM.gov API, retrieved 2026-07-31)

### REQ-006 [DIRECT] Uncrewed tactical autonomy and robotic manipulation
The solution shall be an uncrewed system employing "uncrewed tactical autonomy and robotic manipulation designed or adapted for military recovery operations."
Source: Introduction (verbatim quote). (SAM.gov API, retrieved 2026-07-31)

### REQ-007 [DIRECT] Robust, ruggedized construction for contested environments
The solution shall be "robust, ruggedized ... capable of or, adaptable to, executing complex recovery tasks in contested, degraded, and operationally demanding environments."
Source: Introduction (verbatim quote). (SAM.gov API, retrieved 2026-07-31)

### REQ-008 [DIRECT] Low-logistics footprint
The solution shall be an "advanced, low-logistics" solution that reduces "the overall resource demand, personnel footprint, and exposure time required to execute recovery missions" under DDIL network conditions.
Source: Introduction (verbatim quote). (SAM.gov API, retrieved 2026-07-31)

### REQ-009 [DIRECT] Platform approach: modified existing platform or new system
The solution may be either a modification to an existing Army platform or an entirely separate system ("We are open to modifications to existing Army platforms or entire separate systems").
Source: Introduction (verbatim quote). (SAM.gov API, retrieved 2026-07-31)

### REQ-010 [DIRECT] Enable continuous recovery operations
The solution shall "enhance the Army's ability to conduct continuous recovery operations," addressing the stated constraint that current missions "are fundamentally constrained by human endurance limits."
Source: Introduction and Problem Statement (verbatim quotes). (SAM.gov API, retrieved 2026-07-31)

## Inferred requirements (WyZen interpretation — not stated by the Army)

### REQ-011 [INFERRED] Onboard (edge) autonomy without reliance on persistent connectivity
Because Q4 requires completing navigation and rigging when communications are degraded or denied (paraphrase of Q4), the autonomy stack — perception, planning, manipulation control, and mission logic — must execute onboard the vehicle without a persistent network link or remote teleoperation. The Army asked "how"; it did not prescribe onboard compute.
Source: inference from Q4 and Problem Statement DDIL language. (SAM.gov API, retrieved 2026-07-31)

### REQ-012 [INFERRED] Perception-based identification and assessment of casualty vehicles
"Find" a disabled, destroyed, or immobilized vehicle (paraphrase of Q1) implies sensing and recognition capability to detect, identify, and discriminate the target vehicle and assess its state/pose well enough to plan an approach and rigging operation. The Army did not specify sensors or methods.
Source: inference from Q1 and Q2. (SAM.gov API, retrieved 2026-07-31)

### REQ-013 [INFERRED] Manipulation of standard recovery equipment and attachment points
An "autonomous rigging operation" (paraphrase of Q2) implies physically handling recovery equipment (e.g., cables/tow apparatus) and engaging attachment points on casualty vehicles, with forces and procedures compatible with Army recovery practice. Specific equipment is not named in the RFI.
Source: inference from Q2 and Introduction ("robotic manipulation"). (SAM.gov API, retrieved 2026-07-31)

### REQ-014 [INFERRED] Terrain assessment and traversability reasoning
Operating amid "inaccessible high ground, unstable soil, severe obstacles" (Q3's examples, quoted) implies the system must assess terrain stability and traversability and plan around obstacles — including judging safe positioning for high-force extraction on unstable ground. The Army stated the environments, not the assessment capability.
Source: inference from Q3. (SAM.gov API, retrieved 2026-07-31)

### REQ-015 [INFERRED] Consistency with Army recovery doctrine (ATP 4-31)
The RFI's sole reference is "Army Technical Publication (ATP) 4-31, Recovery and Battle Damage Assessment and Repair (BDAR)" (verbatim from References section). This implies solutions should map their concept of operations to ATP 4-31 recovery procedures and terminology. The Army did not state compliance as a requirement.
Source: inference from References section. (SAM.gov API, retrieved 2026-07-31)

### REQ-016 [INFERRED] Survivability considerations for contested environments
The Problem Statement's rationale — recovery "expose[s] Soldiers to adversarial threats" in "contested environments" (verbatim fragments) — implies the uncrewed system itself will operate under adversarial threat and should be designed with survivability/expendability trade-offs in mind. The RFI does not state survivability requirements.
Source: inference from Problem Statement. (SAM.gov API, retrieved 2026-07-31)

---

## RFI response constraints (programmatic, not system requirements) [DIRECT]

From the Response Instructions (verbatim source in RFI_ACC-APG.md; SAM.gov API, retrieved 2026-07-31):
- Cover page with Company Name, Address, Primary Point of Contact with phone number and email address.
- Max 750 words per question; graphics and diagrams encouraged and excluded from the word count.
- Single PDF file, emailed to unmanned-ground-recovery@aal.army by 11:59 AM CT, 31 July 2026.
- Respondents may answer all or only a portion of the questions.

## Summary

- Total requirements: 16
- [DIRECT]: 10 (REQ-001 through REQ-010)
- [INFERRED]: 6 (REQ-011 through REQ-016)
- All four Army questions were retrieved verbatim from the SAM.gov API on 2026-07-31.
