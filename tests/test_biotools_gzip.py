import gzip

from mycotools.lib.biotools import fa2dict, fa2dict_accs, gff2list, open_text

FA = ">p1 first\nMKV\nLL\n>p2\nAAA\n"
GFF = (
    "##gff-version 3\n"
    "c1\tfunannotate\tgene\t1\t99\t.\t+\t.\tID=G1;\n"
    "c1\tfunannotate\tmRNA\t1\t99\t.\t+\t.\tID=G1-T1;Parent=G1;\n"
)


def _write(path, text, gz):
    if gz:
        with gzip.open(path, "wt") as out:
            out.write(text)
    else:
        path.write_text(text)


def test_open_text_plain_and_gzip(tmp_path):
    for name, gz in (("a.txt", False), ("a.txt.gz", True)):
        p = tmp_path / name
        _write(p, "hello\n", gz)
        with open_text(str(p)) as f:
            assert f.read() == "hello\n"


def test_fa2dict_reads_gzip_like_plain(tmp_path):
    plain, gz = tmp_path / "a.fa", tmp_path / "a.fa.gz"
    _write(plain, FA, False)
    _write(gz, FA, True)
    assert fa2dict(str(plain)) == fa2dict(str(gz))
    assert fa2dict(str(gz))["p1"]["sequence"] == "MKVLL"


def test_fa2dict_accs_reads_gzip(tmp_path):
    gz = tmp_path / "a.fa.gz"
    _write(gz, FA, True)
    assert list(fa2dict_accs(str(gz), accs={"p2"})) == ["p2"]


def test_gff2list_reads_gzip_like_plain(tmp_path):
    plain, gz = tmp_path / "a.gff3", tmp_path / "a.gff3.gz"
    _write(plain, GFF, False)
    _write(gz, GFF, True)
    assert gff2list(str(plain)) == gff2list(str(gz))
    assert [e["type"] for e in gff2list(str(gz))] == ["gene", "mRNA"]
