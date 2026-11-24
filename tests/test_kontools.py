import pytest

from mycotools.lib.kontools import FatalError, exit_on_fatal, findExecs, getColors


def test_exit_on_fatal_uses_code(capsys):
    @exit_on_fatal
    def cli():
        raise FatalError("boom", 7)

    with pytest.raises(SystemExit) as e:
        cli()
    assert e.value.code == 7
    assert "boom" in capsys.readouterr().err


def test_exit_on_fatal_passes_return_value():
    @exit_on_fatal
    def cli():
        return 5

    assert cli() == 5


def test_default_arguments_not_shared():
    a = getColors(3, rgb=True)
    b = getColors(3, rgb=True)
    assert a == b


def test_findexecs_missing_not_fatal():
    assert findExecs(["definitely_not_a_real_binary_xyz"], verbose=False) is not None


def test_acq_forbid_omes_is_shared():
    import mycotools.predb2mtdb as p
    import mycotools.update_mtdb as u

    assert u.acq_forbid_omes is p.acq_forbid_omes


def test_download_helpers_are_shared():
    import mycotools.gff2seq as g
    import mycotools.ncbiDwnld as n
    import mycotools.ncbi_dwnld_fallback as f
    import mycotools.utils.gtf2gff3 as t

    assert f.ncbidb2df is n.ncbidb2df
    assert f.prepare_folders is n.prepare_folders
    assert t.sortGene is g.sortGene
