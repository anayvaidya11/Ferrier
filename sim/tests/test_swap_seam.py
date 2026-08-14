"""The mr_v1 swap seam through the multiprocess runner (run_sweep
curve_sets=...).

Worker processes start with a fresh interpreter, so the parent's curve
registry (only prior_v1 at import time) must be re-populated per worker.
Found during the item-2 swap rehearsal (2026-08-14): without this seam a
multi-worker mr_v1 sweep dies at inject's curves.get(). The gap stays
here as a tested failure mode, not folklore.
"""
import dataclasses
import json

import pytest

from wyzantium_sim.doe import runner as doe_runner
from wyzantium_sim.perception import curves

from tests.test_doe_runner import CHEAP, cheap_plan


def _test_set(name="test_swap_v1"):
    return dataclasses.replace(curves.PRIOR_V1, name=name,
                               angle_falloff_exponent=2.0)


def _plan_on(curve_set_name, n=2):
    return tuple(
        dataclasses.replace(p, sweep_point={**p.sweep_point,
                                            "curve_set": curve_set_name})
        for p in cheap_plan(n))


def _header(path):
    return json.loads(path.read_text().splitlines()[0])


class TestSwapSeam:
    def test_multiworker_sweep_on_registered_set(self, tmp_path):
        cs = _test_set()
        try:
            result = doe_runner.run_sweep(
                _plan_on(cs.name), tmp_path, workers=2, curve_sets=(cs,))
            assert result.ran == 2
            for p in result.paths:
                sp = _header(p)["sweep_point"]
                assert sp["curve_set"] == cs.name
        finally:
            curves.unregister(cs.name)

    def test_multiworker_sweep_without_seam_fails(self, tmp_path):
        # The pre-seam behavior, pinned: an unregistered set dies in the
        # worker (KeyError from curves.get) and run_sweep surfaces it.
        with pytest.raises(KeyError):
            doe_runner.run_sweep(_plan_on("test_swap_unregistered"),
                                 tmp_path, workers=2)

    def test_same_name_different_values_refused(self, tmp_path):
        cs = _test_set()
        curves.register(cs)
        try:
            impostor = dataclasses.replace(cs, lux_knee=99.0)
            with pytest.raises(ValueError, match="never edited in place"):
                doe_runner.run_sweep(_plan_on(cs.name), tmp_path,
                                     workers=1, curve_sets=(impostor,))
        finally:
            curves.unregister(cs.name)

    def test_singleworker_path_registers_too(self, tmp_path):
        cs = _test_set("test_swap_v1_solo")
        try:
            result = doe_runner.run_sweep(
                _plan_on(cs.name, n=1), tmp_path, workers=1,
                curve_sets=(cs,))
            assert result.ran == 1
            assert curves.get(cs.name) == cs
        finally:
            curves.unregister(cs.name)

    def test_prior_v1_callers_unaffected(self, tmp_path):
        result = doe_runner.run_sweep(cheap_plan(1), tmp_path, workers=1)
        assert result.ran == 1
        assert _header(result.paths[0])["sweep_point"]["curve_set"] \
            == "prior_v1"
