import itertools
import pathlib
import shlex
import subprocess
import time

import freezegun
import pytest
from pytest_lazy_fixtures import lf

import csv2ofx.main

samples = [
    (["-oq"], "default.csv", "default.qif"),
    (["-oq", "-m split_account"], "default.csv", "default_w_splits.qif"),
    (["-oqc Description", "-m xero"], "xero.csv", "xero.qif"),
    (["-oq", "-m mint"], "mint.csv", "mint.qif"),
    (["-oq", "-m mint_extra"], "mint_extra.csv", "mint_extra.qif"),
    (["-oq", "-m mint_headerless"], "mint_headerless.csv", "mint.qif"),
    (["-oqs20150613", "-e20150614", "-m mint"], "mint.csv", "mint_alt.qif"),
    (["-oe 20150908"], "default.csv", "default.ofx"),
    (["-o", "-m split_account"], "default.csv", "default_w_splits.ofx"),
    (["-o", "-m mint"], "mint.csv", "mint.ofx"),
    (["-oq", "-m creditunion"], "creditunion.csv", "creditunion.qif"),
    (
        ["-o", "-m stripe", "-e", "20210505"],
        "stripe-default.csv",
        "stripe-default.ofx",
    ),
    (
        ["-o", "-m stripe", "-e", "20210505"],
        "stripe-all.csv",
        "stripe-all.ofx",
    ),
    (["-oq", "-m stripe"], "stripe-default.csv", "stripe-default.qif"),
    (["-oq", "-m stripe"], "stripe-all.csv", "stripe-all.qif"),
    (
        ["-E windows-1252", "-m gls", "-e 20171111", "-o"],
        "gls.csv",
        "gls.ofx",
    ),
    (
        ["-o", "-m pcmastercard", "-e 20190120"],
        "pcmastercard.csv",
        "pcmastercard.ofx",
    ),
    # (
    #     # N.B. input file obtained by pre-processing with
    #     #    bin/csvtrim ubs-ch-fr.csv > ubs-ch-fr_trimmed.csv
    #     ["-oq", "-m ubs-ch-fr"], "ubs-ch-fr_trimmed.csv", "ubs-ch-fr.qif"
    # ),
    (
        ["-o", "-m ingesp", "-e 20221231"],
        "ingesp.csv",
        "ingesp.ofx",
    ),
    (
        ["-o", "-m schwabchecking", "-e 20220905"],
        "schwab-checking.csv",
        "schwab-checking.ofx",
    ),
    (
        ["-o", "-M", "-m schwabchecking", "-e 20220905"],
        "schwab-checking.csv",
        "schwab-checking-msmoney.ofx",
    ),
    (
        ["-o", "-m schwabchecking", "-e 20220905"],
        "schwab-checking-baltest-case1.csv",
        "schwab-checking-baltest-case1.ofx",
    ),
    (
        ["-o", "-m schwabchecking", "-e 20220905"],
        "schwab-checking-baltest-case2.csv",
        "schwab-checking-baltest-case2.ofx",
    ),
    (
        ["-o", "-m schwabchecking", "-e 20220905"],
        "schwab-checking-baltest-case3.csv",
        "schwab-checking-baltest-case3.ofx",
    ),
    (
        ["-o", "-m schwabchecking", "-e 20220905"],
        "schwab-checking-baltest-case4.csv",
        "schwab-checking-baltest-case4.ofx",
    ),
    (
        ["-o", "-m schwabchecking", "-e 20220905"],
        "schwab-checking-baltest-case5.csv",
        "schwab-checking-baltest-case5.ofx",
    ),
    (
        ["-o", "-m schwabchecking", "-e 20220905"],
        "schwab-checking-baltest-case6.csv",
        "schwab-checking-baltest-case6.ofx",
    ),
    (
        ["-o", "-m schwabchecking", "-e 20220905"],
        "schwab-checking-baltest-case7.csv",
        "schwab-checking-baltest-case7.ofx",
    ),
    (
        ["-o", "-m amazon", "-e 20230604"],
        lf("amazon_inputs"),
        "amazon.ofx",
    ),
    (
        ["-o", "-m payoneer", "-e 20220905"],
        "payoneer.csv",
        "payoneer.ofx",
    ),
    (
        ['-m', 'n26'],
        'n26-fr.csv',
        'n26.ofx',
    ),
]


@pytest.fixture
def amazon_inputs(monkeypatch):
    # for Amazon import; excludes transaction 3/3
    monkeypatch.setenv("AMAZON_EXCLUDE_CARDS", "9876")
    # clear the purchases account if set
    monkeypatch.delenv("AMAZON_PURCHASES_ACCOUNT", raising=False)
    return "amazon.csv"


data = pathlib.Path('data')


def flatten_opts(opts):
    return list(param for group in opts for param in shlex.split(group))


@pytest.mark.parametrize(['opts', 'in_filename', 'out_filename'], samples)
@freezegun.freeze_time("2016-10-31 11:29:08")
def test_sample(opts, in_filename, out_filename, capsys, monkeypatch):
    monkeypatch.setattr(csv2ofx.main, '_time_from_file', lambda path: time.time())
    arguments = [str(data / 'test' / in_filename)]
    command = list(itertools.chain(['csv2ofx'], flatten_opts(opts), arguments))
    with pytest.raises(SystemExit) as exc:
        csv2ofx.main.run(command[1:])
    # Success - exit code 0
    assert exc.value.code == 0

    expected = data.joinpath("converted", out_filename).read_text(encoding='utf-8')
    assert capsys.readouterr().out == expected, (
        f"Unexpected output from {subprocess.list2cmdline(command)}"
    )


def test_help():
    """
    Assert help command completes and is present in the README.
    """
    out = subprocess.check_output(['csv2ofx', '--help'], text=True)
    assert out


@pytest.mark.xfail("sys.version_info < (3, 13)")
def test_help_in_readme():
    out = subprocess.check_output(['csv2ofx', '--help'], text=True)
    readme = pathlib.Path('README.md').read_text()
    assert out in readme, "README help is stale, please update."
