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


def test_run_mmseqs_clusters_gzipped_proteomes(tmp_path):
    """BFD-style .faa.gz proteomes: soft_main must keep the .gz suffix."""
    import gzip

    src = tmp_path / "src"
    src.mkdir()
    _write_proteomes(src)
    wrk = tmp_path / "wrk"
    wrk.mkdir()
    paths = {}
    for ome in ("a", "b"):
        gz = src / f"{ome}.proteins.fa.gz"
        with gzip.open(gz, "wt") as out:
            out.write((src / "faa" / f"{ome}.faa").read_text())
        paths[ome] = str(gz)

    class FakeDB(dict):
        def set_index(self, col):
            return self

    db = FakeDB({o: {"faa": p} for o, p in paths.items()})
    res = db2hgs.run_mmseqs(db, str(wrk) + "/", cpus=2)
    assert sum(1 for _ in open(res)) == 40
    links = sorted(p.name for p in (wrk / "faa").iterdir())
    assert links == ["a.faa.gz", "b.faa.gz"]
