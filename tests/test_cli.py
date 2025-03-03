import pathlib
import subprocess


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
