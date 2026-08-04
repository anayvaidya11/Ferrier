"""Newton (Warp) adapter stub for the ContactEngine protocol (T4c).

Newton is the primary engine of record (D-007, ARCH §4); it requires
CUDA and cannot run on the M4 (PHASE1_PLAN §2). This adapter is written
locally so the conformance suite is engine-parameterized from day one; the
implementation lands on the first provisioned instance, where the ARCH §4
fallback test decides Newton vs MuJoCo. Until then, load() raises and the
Newton-parameterized conformance cases skip locally.
"""

from __future__ import annotations

from wyzantium_sim.contact.engine import SolverSettings, StepResult, T1ModelSpec


class NewtonEngine:
    """ContactEngine adapter over newton/warp — provisioned-instance only."""

    @property
    def engine_id(self) -> dict:
        import newton
        return {"name": "newton", "version": newton.__version__}

    def load(self, spec: T1ModelSpec, solver: SolverSettings) -> None:
        try:
            import newton  # noqa: F401
        except ImportError as exc:
            raise ImportError(
                "Newton (Warp) requires CUDA and is unavailable locally; "
                "run on the provisioned instance (PHASE1_PLAN §2, ARCH §4)."
            ) from exc
        raise NotImplementedError(
            "NewtonEngine.load lands with the first provisioned instance "
            "(T4c Newton half; ARCH §4 conformance decides Newton vs MuJoCo).")

    def set_state(self, handoff) -> None:
        raise NotImplementedError

    def step(self, dt: float) -> StepResult:
        raise NotImplementedError

    def state(self) -> StepResult:
        raise NotImplementedError
