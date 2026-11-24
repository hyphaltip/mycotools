import os
import pathlib

import pytest

from mycotools.lib.dbtools import mtdb

REF = pathlib.Path(__file__).resolve().parents[1] / "test" / "ust.mtdb"


@pytest.fixture
def db():
    return mtdb(str(REF), add_paths=False)


def _n_rows():
    return sum(1 for x in REF.read_text().splitlines() if x.strip() and not x.startswith("#"))


def test_reads_all_rows(db):
    assert len(db["ome"]) == _n_rows() == 42


def test_columns_are_equal_length(db):
    lengths = {len(db[c]) for c in mtdb.columns}
    assert lengths == {42}


def test_taxonomy_parsed_and_genus_species_added(db):
    tax = db["taxonomy"][0]
    assert isinstance(tax, dict)
    assert tax["genus"] == db["genus"][0]
    assert tax["species"] == f"{db['genus'][0]} {db['species'][0]}"
    assert tax["kingdom"] == "Fungi"


def test_set_index_roundtrip(db):
    indexed = db.set_index("ome")
    assert set(indexed.keys()) == set(db["ome"])
    flat = indexed.reset_index()
    assert sorted(flat["ome"]) == sorted(db["ome"])


def test_invalid_index_rejected(db):
    with pytest.raises(KeyError):
        db.set_index("genus")


def test_df2db_roundtrip(db, tmp_path, monkeypatch):
    # df2db reads these variables unconditionally (see audit notes)
    for var in ("MYCOFNA", "MYCOFAA", "MYCOGFF3"):
        monkeypatch.setenv(var, str(tmp_path / var) + "/")
    out = tmp_path / "out.mtdb"
    db.df2db(str(out), paths=True)
    back = mtdb(str(out), add_paths=False)
    assert sorted(back["ome"]) == sorted(db["ome"])
    ome = db["ome"][0]
    i, j = db["ome"].index(ome), back["ome"].index(ome)
    assert back["taxonomy"][j]["family"] == db["taxonomy"][i]["family"]


def test_append_does_not_share_state(db):
    new = db.set_index("ome").append({"ome": "zzz1", "genus": "G", "species": "s"})
    assert "zzz1" in new
    assert "zzz1" not in db["ome"]
