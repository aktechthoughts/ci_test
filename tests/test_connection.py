# -*- coding: utf-8 -*-
"""Test connecting to database"""


import pytest


@pytest.mark.skip(reason="Disabling Docker as no real tests yet")
def test__create_table__dummy__no_error(exaplus):
    assert exaplus("tests/sql_samples/sandbox_ddl.sql") == 0


@pytest.mark.skip(reason="Disabling Docker as no real tests yet")
def test__insert__to_dummy__no_error(exaplus):
    assert exaplus("tests/sql_samples/sandbox_etl.sql") == 0


@pytest.mark.skip(reason="Disabling Docker as no real tests yet")
def test__select__from_dummy__no_error(query):
    result = query("SELECT * FROM SANDBOX.DUMMY_TABLE WHERE TEST_DECIMAL = 31337")
    assert result["TEST_STRING"][0] == "It works"
