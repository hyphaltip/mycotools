import os

from mycotools.db2files import soft_main


class FakeDB(dict):
    def set_index(self, col):
        return self


def test_soft_main_keeps_gz_suffix(tmp_path):
    plain = tmp_path / "p.faa"
    plain.write_text(">x\nM\n")
    gz = tmp_path / "g.proteins.fa.gz"
    gz.write_bytes(b"")
    out = tmp_path / "out"
    out.mkdir()
    db = FakeDB({"o1": {"faa": str(plain)}, "o2": {"faa": str(gz)}})
    soft_main(["faa"], db, str(out) + "/")
    assert sorted(os.listdir(out / "faa")) == ["o1.faa", "o2.faa.gz"]
