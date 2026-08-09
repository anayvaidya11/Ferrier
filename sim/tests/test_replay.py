"""T11 gate: replay bit-identical; artifact generated from a record,
labeled simulated, carries trial_id (A-007)."""

import json

import pytest

from wyzantium_sim import scenarios, trial
from wyzantium_sim.contact.mujoco_engine import MuJoCoEngine
from wyzantium_sim.doe import tiers
from wyzantium_sim.replay import render_artifact, replay_record


@pytest.fixture(scope="module")
def record(tmp_path_factory):
    out = tmp_path_factory.mktemp("rec")
    nominal = scenarios.build_sweep_point(
        **tiers.load_nominal()["sweep_point"])
    return trial.run_trial(20260809, nominal, MuJoCoEngine(), "prior_v1",
                           out_dir=out)


class TestVerify:
    def test_replay_is_bit_identical(self, record, tmp_path):
        v = replay_record(record, out_dir=tmp_path)
        assert v.status == "identical"
        assert v.n_diff_lines == 0
        assert v.replayed_path.read_bytes() == record.read_bytes()

    def test_tampered_record_diverges(self, record, tmp_path):
        lines = record.read_text(encoding="utf-8").splitlines()
        result = json.loads(lines[-1])
        result["outcome"] = "IS8-4" if result["outcome"] != "IS8-4" \
            else "success"
        tampered = tmp_path / record.name
        tampered.write_text("\n".join(lines[:-1] + [json.dumps(result)])
                            + "\n", encoding="utf-8")
        v = replay_record(tampered, out_dir=tmp_path / "replayed")
        assert v.status == "diverged"
        assert v.n_diff_lines >= 1


class TestArtifact:
    def test_artifact_labeled_and_traceable(self, record, tmp_path):
        gif, sidecar = render_artifact(record, tmp_path, max_frames=24,
                                       fps=12)
        assert gif.is_file() and gif.stat().st_size > 0
        assert "simulated" in gif.name
        meta = json.loads(sidecar.read_text(encoding="utf-8"))
        header = json.loads(
            record.read_text(encoding="utf-8").splitlines()[0])
        assert meta["label"] == "simulated"
        assert meta["trial_id"] == header["trial_id"]
        assert meta["trial_id"] in gif.name
        assert meta["source_record"] == str(record)
