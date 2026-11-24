import ast
import pathlib

from mycotools.db2hgs import id_near_schgs

OMES = {"a", "b", "c", "d"}


def _hg2gene():
    return {
        "hg_single": ["a_1", "b_1", "c_1", "d_1"],  # single copy, all genomes
        "hg_dup": ["a_2", "a_3", "b_2", "b_3", "c_2", "c_3", "d_2", "d_3"],  # 2 copies each
        "hg_partial": ["a_4", "b_4", "c_4", "c_5"],  # not in d
    }


def test_all_genome_single_copy_found_with_fraction_one():
    schgs, near, stats, full, _ = id_near_schgs(
        _hg2gene(), OMES, max_hgs=100, max_median=1, max_stdev=0.2, min_genomes=1
    )
    assert schgs == ["hg_single"]
    assert "hg_partial" not in near


def test_count_instead_of_fraction_finds_nothing():
    # min_genomes is a fraction of genomes: passing the genome count (4) can never match
    schgs, near, *_ = id_near_schgs(
        _hg2gene(), OMES, max_hgs=100, max_median=1, max_stdev=0.2, min_genomes=len(OMES)
    )
    assert schgs == [] and near == []


def test_microsyntree_passes_a_fraction():
    src = pathlib.Path(__file__).resolve().parents[1] / "mycotools" / "db2microsyntree.py"
    for node in ast.walk(ast.parse(src.read_text())):
        if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "id_near_schgs":
            for kw in node.keywords:
                if kw.arg == "min_genomes":
                    assert isinstance(kw.value, ast.Constant) and kw.value.value <= 1
