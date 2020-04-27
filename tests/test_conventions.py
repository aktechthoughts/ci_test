"""Testing standard naming conventions"""

import re

import pytest
from sqlparse import tokens
from sqlparse.keywords import KEYWORDS_COMMON
from sqlparse.tokens import DDL, DML

from .helpers import (
    get_fobj,
    get_sql_files,
    parse_sql,
    TODO_PATTERN,
    assert_sql_contains_only,
    check_stmt,
)

KEYWORDS_COMMON["TRUNCATE"] = tokens.Keyword.DDL
KEYWORDS_COMMON["IMPORT"] = tokens.Keyword.DDL
DDL_FILES = get_sql_files(root="ddl")
TABLES = get_sql_files(root="ddl", filterl=["tables"])
BASE_TABLES = [name for name in TABLES if TODO_PATTERN not in name]
TODO_TABLES = [name for name in TABLES if TODO_PATTERN in name]
VIEWS = get_sql_files(root="ddl", filterl=["views"])
ALL_EXCEPT = [
    get_sql_files(root=".", exclude=[".ci", ".build", "tests", "extract"]),
    get_sql_files(root=".", exclude=["tests"]),
]


@pytest.mark.parametrize("path", DDL_FILES)
def test_object_name_screaming_snake_true(path):
    _, _, schema = parse_sql(path)
    name = schema.get_real_name()

    assert name.replace(
        "_", ""
    ).isalnum(), "Object names should be alphanumeric with '_' as separators."
    assert (
        name.isupper()
    ), f"Wrong object name: {name}\nObject names should be all uppercase"
    assert name[0].isalpha(), "Object names should start with a character."


@pytest.mark.skip(reason="To be activated with TODO rollout.")
@pytest.mark.parametrize("path", BASE_TABLES)
def test_base_has_only_one_object(path):
    _, stmts, _ = parse_sql(path, DDL, DML)

    assert len(stmts) == 1, "Only one DDL statement is allowed in base SQL"


@pytest.mark.parametrize("path", DDL_FILES)
def test_each_stmt_ends_with_semicolon(path):
    _, stmts, _ = parse_sql(path, DDL, DML)
    assert all(
        [stmt.strip().endswith(";") for stmt in stmts]
    ), "All SQL statements must end with a semicolon."


@pytest.mark.parametrize("path", DDL_FILES)
def test_ddl_has_correct_name(path):
    _, _, schema = parse_sql(path, DDL, DML)

    assert re.fullmatch(
        r"(\w+[.]\w+)", f"{schema.get_parent_name()}.{schema.get_real_name()}"
    ), "Object (schema) name should be separated by dot"
    assert re.fullmatch(
        get_fobj(path), schema.get_real_name(), re.IGNORECASE
    ), f"Wrong object name {schema.get_real_name()}\n \
    Filename and object name should be the same: file name <> schema object name,\n \
    got {get_fobj(path)} <> {schema.get_real_name()}"
    assert re.fullmatch(
        get_fobj(path, schema=True), schema.get_parent_name(), re.IGNORECASE
    ), f"Wrong schema parent name {schema.get_parent_name()}\n \
    Schema directory name and schema parent name should be the same:\n \
    schema directory name <> schema parent name,\n \
    got {get_fobj(path, schema=True)} <> {schema.get_parent_name()}"


@pytest.mark.parametrize("path", DDL_FILES)
def test_no_delete_stmt(path):
    assert_sql_contains_only(
        path, ["DELETE FROM", "DROP TABLE", "TRUNCATE TABLE"], exclude=True
    )


@pytest.mark.skip(reason="To be activated with TODO rollout.")
@pytest.mark.parametrize("path", BASE_TABLES)
def test_base_contains_only_create(path):
    assert_sql_contains_only(path, ["CREATE TABLE IF NOT EXISTS"])


@pytest.mark.parametrize("path", BASE_TABLES)
def test_base_contains_only_create_if_not_exists(path):
    _, stmts, _ = parse_sql(path, DDL)

    stmt = stmts[0]
    check = check_stmt(stmt, ["CREATE TABLE IF NOT EXISTS"], False)
    assert (
        check
    ), f"{path} should contain only CREATE TABLE IF NOT EXISTS as a first statement!"


@pytest.mark.parametrize("path", TODO_TABLES)
def test_todo_contains_only_alter(path):
    assert_sql_contains_only(path, ["ALTER TABLE"])


@pytest.mark.parametrize("path", TODO_TABLES)
def test_todo_has_correct_sequence_number(path):
    seq_num = path.split(".")[2]
    assert (
        len(seq_num) == 3
    ), "todo filename has to follow naming convention: \
    {TABLE_NAME}.todo.{SEQ}.sql where SEQ is a 3-digit sequence number"
    assert seq_num.isdigit(), "todo sequence suffix is not a proper number"


@pytest.mark.parametrize("path", VIEWS)
def test_views_dir_contains_only_views(path):
    assert_sql_contains_only(path, ["CREATE OR REPLACE VIEW"])


@pytest.mark.parametrize("path", ALL_EXCEPT[0])
def test_no_sql_outside_of_ddl_and_etl(path):
    assert re.search(
        r"^(ddl|etl)", path, re.IGNORECASE
    ), "SQL files should be found only in the following folders: ddl, etl"


@pytest.mark.parametrize("path", ALL_EXCEPT[1])
def test_passwords_search_no_passwords_in_connections(path):
    assert_sql_contains_only(path, ["USER IDENTIFIED BY"], exclude=True)
