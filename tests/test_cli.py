import itertools
import pathlib
import shlex
import subprocess

import pytest

MINT_ALT_OPTS = ["-oqs20150613", "-e20150614", "-m mint"]
SERVER_DATE = "-D 20161031112908"
SPLIT_OPTS = ["-o", "-m split_account", SERVER_DATE]

samples = [
    (["-oq"], "default.csv", "default.qif"),
    (["-oq", "-m split_account"], "default.csv", "default_w_splits.qif"),
    (["-oqc Description", "-m xero"], "xero.csv", "xero.qif"),
    (["-oq", "-m mint"], "mint.csv", "mint.qif"),
    (["-oq", "-m mint_extra"], "mint_extra.csv", "mint_extra.qif"),
    (["-oq", "-m mint_headerless"], "mint_headerless.csv", "mint.qif"),
    (MINT_ALT_OPTS, "mint.csv", "mint_alt.qif"),
    (["-oe 20150908", SERVER_DATE], "default.csv", "default.ofx"),
    (SPLIT_OPTS, "default.csv", "default_w_splits.ofx"),
    (["-o", "-m mint", SERVER_DATE], "mint.csv", "mint.ofx"),
    (["-oq", "-m creditunion"], "creditunion.csv", "creditunion.qif"),
    (
        ["-o", "-m stripe", "-e", "20210505", SERVER_DATE],
        "stripe-default.csv",
        "stripe-default.ofx",
    ),
    (
        ["-o", "-m stripe", "-e", "20210505", SERVER_DATE],
        "stripe-all.csv",
        "stripe-all.ofx",
    ),
    (["-oq", "-m stripe"], "stripe-default.csv", "stripe-default.qif"),
    (["-oq", "-m stripe"], "stripe-all.csv", "stripe-all.qif"),
    (
        ["-E windows-1252", "-m gls", SERVER_DATE, "-e 20171111", "-o"],
        "gls.csv",
        "gls.ofx",
    ),
    (
        ["-o", "-m pcmastercard", "-e 20190120", SERVER_DATE],
        "pcmastercard.csv",
        "pcmastercard.ofx",
    ),
    # (
    #     # N.B. input file obtained by pre-processing with
    #     #    bin/csvtrim ubs-ch-fr.csv > ubs-ch-fr_trimmed.csv
    #     ["-oq", "-m ubs-ch-fr"], "ubs-ch-fr_trimmed.csv", "ubs-ch-fr.qif"
    # ),
    (
        ["-o", "-m ingesp", "-e 20221231", SERVER_DATE],
        "ingesp.csv",
        "ingesp.ofx",
    ),
    (
        ["-o", "-m schwabchecking", "-e 20220905", SERVER_DATE],
        "schwab-checking.csv",
        "schwab-checking.ofx",
    ),
    (
        ["-o", "-M", "-m schwabchecking", "-e 20220905", SERVER_DATE],
        "schwab-checking.csv",
        "schwab-checking-msmoney.ofx",
    ),
    (
        ["-o", "-m schwabchecking", "-e 20220905", SERVER_DATE],
        "schwab-checking-baltest-case1.csv",
        "schwab-checking-baltest-case1.ofx",
    ),
    (
        ["-o", "-m schwabchecking", "-e 20220905", SERVER_DATE],
        "schwab-checking-baltest-case2.csv",
        "schwab-checking-baltest-case2.ofx",
    ),
    (
        ["-o", "-m schwabchecking", "-e 20220905", SERVER_DATE],
        "schwab-checking-baltest-case3.csv",
        "schwab-checking-baltest-case3.ofx",
    ),
    (
        ["-o", "-m schwabchecking", "-e 20220905", SERVER_DATE],
        "schwab-checking-baltest-case4.csv",
        "schwab-checking-baltest-case4.ofx",
    ),
    (
        ["-o", "-m schwabchecking", "-e 20220905", SERVER_DATE],
        "schwab-checking-baltest-case5.csv",
        "schwab-checking-baltest-case5.ofx",
    ),
    (
        ["-o", "-m schwabchecking", "-e 20220905", SERVER_DATE],
        "schwab-checking-baltest-case6.csv",
        "schwab-checking-baltest-case6.ofx",
    ),
    (
        ["-o", "-m schwabchecking", "-e 20220905", SERVER_DATE],
        "schwab-checking-baltest-case7.csv",
        "schwab-checking-baltest-case7.ofx",
    ),
    (
        ["-o", "-m amazon", "-e 20230604", SERVER_DATE],
        "amazon.csv",
        "amazon.ofx",
    ),
    (
        ["-o", "-m payoneer", "-e 20220905", SERVER_DATE],
        "payoneer.csv",
        "payoneer.ofx",
    ),
]


@pytest.fixture(autouse=True)
def amazon_env(monkeypatch):
    # for Amazon import; excludes transaction 3/3
    monkeypatch.setenv("AMAZON_EXCLUDE_CARDS", "9876")
    # clear the purchases account if set
    monkeypatch.delenv("AMAZON_PURCHASES_ACCOUNT", raising=False)


data = pathlib.Path('data')


def flatten_opts(opts):
    return list(param for group in opts for param in shlex.split(group))


@pytest.mark.parametrize(['opts', 'in_filename', 'out_filename'], samples)
def test_sample(opts, in_filename, out_filename):
    arguments = [str(data / 'test' / in_filename)]
    command = list(itertools.chain(['csv2ofx'], flatten_opts(opts), arguments))
    proc = subprocess.run(
        command, capture_output=True, text=True, encoding='utf-8', check=True
    )
    output = proc.stdout

    expected = data.joinpath("converted", out_filename).read_text(encoding='utf-8')
    assert output == expected, (
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
