"""T12 — analysis: committed-deliverable curves and windows from record
datasets (PHASE1_PLAN §2). Data only — interpretation stays in
ARCHITECTURE §6."""

from wyzantium_sim.analysis.dataset import (  # noqa
    MixedCurveSetsError, TrialRow, load_dataset,
)
from wyzantium_sim.analysis.curves import (  # noqa
    CONTACT_FAILURE_CLASSES, REFUSAL_CLASSES, attempt_splits,
    outcome_census, refusal_damage, sensitivity,
)
from wyzantium_sim.analysis.feasibility import feasibility  # noqa
