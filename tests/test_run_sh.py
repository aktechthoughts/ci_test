# -*- coding: utf-8 -*-

"""Testing the run.sh scripts"""

import re
from pathlib import Path

import pytest


def test_every_etl_folder_contains_run_sh():
    """Test that every folder (job) contains run.sh file."""
    path = Path("etl")
    dirs = [unit for unit in path.iterdir() if unit.is_dir()]
    files = [dir for dir in dirs if Path(dir / "run.sh").exists()]
    diff = list(map(str, set(dirs).difference(files)))
    is_empty = ", ".join(diff) if diff else False
    assert not is_empty, f"Missing run.sh in: {is_empty}"


@pytest.mark.parametrize("path", [str(path) for path in Path("etl").rglob("run.sh")])
def test_every_run_sh_file_contains_headers(path):
    """Test that every run.sh file contains headers."""
    run_file = Path(path).read_text()
    ptrn = r"\\(author|descr|jira).*"
    assert (
        len(re.findall(ptrn, run_file, re.IGNORECASE)) == 3
    ), "run.sh should contain: author, descr and jira info"


@pytest.mark.skip(reason="To be updated")
@pytest.mark.parametrize("path", [str(path) for path in Path("etl").rglob("run.sh")])
def test_every_run_sh_file_contains_valid_exa_run(path):
    """Test that every run.sh contains valid exa_run execution"""
    # Needed SQL file check + comments + raise an error if there is an incorrect occurence
    run_file = Path(path).read_text()
    ptrn_exarun = r"\n\s*(exa_run)+"
    ptrn_sql = r"(\d*.([a-zA-Z]*|[a-zA-Z]_)*[.][a-zA-Z]{3})"
    ptrn_valid = ptrn_exarun + r"\s*\"*\$+\{*(work_dir)+\}*\/" + ptrn_sql
    assert re.findall(
        ptrn_valid, run_file, re.IGNORECASE
    ), "run.sh should contain valid exa_run."
