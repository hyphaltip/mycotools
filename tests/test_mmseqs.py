import random
import shutil

import pytest

import mycotools.db2hgs as db2hgs
from mycotools.lib.kontools import FatalError

pytestmark = pytest.mark.skipif(shutil.which("mmseqs") is None, reason="mmseqs not installed")


def _write_proteomes(wrk):
    rng = random.Random(1)
    aa = "ACDEFGHIKLMNPQRSTVWY"
    base = ["".join(rng.choice(aa) for _ in range(150)) for _ in range(20)]
    (wrk / "faa").mkdir()
    for ome in ("a", "b"):
        with open(wrk / "faa" / f"{ome}.faa", "w") as out:
            for i, seq in enumerate(base):
                out.write(f">{ome}_{i}\n{seq}\n")


def test_run_mmseqs_clusters_without_shell(tmp_path, monkeypatch):
    _write_proteomes(tmp_path)
    monkeypatch.setattr(db2hgs, "symlink_files", lambda *a, **k: None)
    res = db2hgs.run_mmseqs(None, str(tmp_path) + "/", cpus=2)
    assert sum(1 for _ in open(res)) == 40  # 20 pairs, 2 members each


def test_run_mmseqs_rejects_unknown_binary(tmp_path, monkeypatch):
    monkeypatch.setattr(db2hgs, "symlink_files", lambda *a, **k: None)
    with pytest.raises(OSError):
        db2hgs.run_mmseqs(None, str(tmp_path) + "/", algorithm="rm -rf /")


def test_run_mmseqs_no_proteomes_is_fatal(tmp_path, monkeypatch):
    (tmp_path / "faa").mkdir()
    monkeypatch.setattr(db2hgs, "symlink_files", lambda *a, **k: None)
    with pytest.raises(FatalError):
        db2hgs.run_mmseqs(None, str(tmp_path) + "/")
