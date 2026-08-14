# WyZantium: Ferrier— Autonomous Recovery for Unmanned Ground Fleets

WyZantium builds the autonomous hand that keeps unmanned fleets in the fight: a robot that
goes forward when another robot goes down, and does the physical work a human would
otherwise walk into the kill zone to do. The load-bearing claim: **a standardized
attachment interface turns autonomous battlefield recovery from a research problem
into an engineering problem.** The program's deliverable is a demonstrated and
simulated design plus the evidence it would work — the gap presented to investors is
capital, not physics.

**Status: Phase 0 CLOSED — gate signed 2026-08-02 (P-05), cloud ceiling ratified at
$100 (P-02, A-011). Phase 1 — the docking experiment, a kill gate — is OPEN as of
2026-08-02** (early start per A-011; window ends 30 September). Execution map:
`PHASE1_PLAN.md`.

## Reading order for a new session

1. `MASTER_CONTEXT.md` — canonical: company, plan, rules. **Read the AMENDMENTS
   section; amendments win over body text.**
2. `NO_HARDWARE.md` — procurement law: instruments, not artifacts.
3. `DECISIONS.md` — every design decision, D-001…D-030; specs cite these.
4. `ROADMAP.md` — phase status. Then whatever the task touches below.

## Document map

| File | What it is |
|---|---|
| `COMPENDIUM.md` | Single-file derived reference: the whole project in one document (company, plan, architecture, experiment machine, results, decision digest, diagrams). Sources of truth win over it |
| `INTERFACE_SPEC.md` | The docking target: stud, fiducials, frames, tolerances, failure modes |
| `ARCHITECTURE.md` | Four functions, data flow, real-vs-simulated table, sim + compute plan |
| `WIRE_FORMAT.md` | The one wire contract: target-state stream + deterministic trial records |
| `PHASE1_PARAMETERS.md` | Every Phase 1 parameter with its source; unfilled entries = the open gate |
| `PHASE1_PLAN.md` | Phase 1 execution map: build order, per-task verification gates, schedule, risks |
| `HOLES.md` | Gate ledger: what closed through which door, what remains open |
| `FAILURE_TAXONOMY.md` | IS8 failure rows as classifiable events |
| `MEASUREMENT_REQUESTS.md` | The only channel to physical measurement (MR-001…004) |
| `studies/` | Tradeoff studies and derivations (H-04 funnel compliance — T1 ratified, D-027; H-08 ambiguity model; C-09 value threshold) |
| `CLAIMS.md` | Claims register: no external claim without a row |
| `COST_OF_GAP.md` | Phase 2 scaffold: what the capital buys |
| `PENDING_HUMAN.md` | Everything owed by the human, in one place |
| `research/` | Week 1 primary-source corpus (RFI verbatim, requirements, standards, vendors, follow-on) |

## Labeling convention (MASTER_CONTEXT §4.3 — non-negotiable)

**Measured** (instrument named) / **derived** (arithmetic shown) / **sourced**
(citation checkable) / **extrapolated** / **assumed** / **simulated** / **stub** —
every number carries its label; simulated is labeled simulated, raw is labeled raw,
stub is labeled stub. A blocked analysis that names its blocker is a success; a
completed analysis resting on a fabricated number is the failure this program exists
to prevent.
