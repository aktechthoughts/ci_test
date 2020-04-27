# -*- coding: utf-8 -*-

"""Testing the shell scripts"""

import os
import subprocess
from glob import glob

import pytest

ARTEFACTS_PATH = "artefacts"


@pytest.mark.parametrize(
    "script_path", glob("**/*.sh", recursive=True) + glob(".ci/*.sh")
)
def test__lint_scipts__shellcheck__no_findings(script_path):
    return_code = subprocess.call(
        'shellcheck --enable=all "%s" 2>&1 | tee "%s"/shellcheck.log'
        % (script_path, ARTEFACTS_PATH),
        shell=True,
    )
    assert return_code == 0, "See shellcheck.log in artefacts for more details"


@pytest.mark.parametrize("script_path", glob("**/*.sh", recursive=True))
def test__style__beautysh__no_changes(script_path):
    return_code = subprocess.call(
        'beautysh --tab --backup "%s"' % script_path, shell=True
    )
    assert return_code == 0

    backup_file = script_path + ".bak"
    styling_required = os.path.isfile(backup_file)
    if styling_required:
        # Clean for next run
        os.remove(backup_file)
    assert not styling_required, "Please apply 'make style'"
