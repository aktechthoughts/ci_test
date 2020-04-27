"""Pytest helpers"""

import re
from functools import lru_cache
from pathlib import Path, PurePath
from itertools import chain
from sqlparse.sql import IdentifierList
from sqlparse.tokens import DDL

import sqlparse


TODO_PATTERN = ".todo"


@lru_cache(maxsize=None)
def cached_parse(sql):
    """
    Cached sqlparse.parse
    """
    return sqlparse.parse(sql)


def get_sql_files(root=".", filterl=None, exclude=None):
    """Get a list of SQL file paths based on parameters.

    Args:
        root (str):   A name of a parent directory where start searching.
        filterl (:list:`str`): A list of directory names where search for SQL file paths
        exclude (:list:`str`): A list of directory names to exclude from search

    Returns:
        (:list:`str`): Filtered list of SQL file paths.
    """
    paths = Path(root).rglob("*.sql")

    if root:
        if filterl:
            return [
                str(path)
                for path in paths
                if any(
                    re.match(path.parts[-2], name, re.IGNORECASE) for name in filterl
                )
            ]
        if exclude:
            return [
                str(path)
                for path in paths
                if not any(
                    re.match(path.parts[0], name, re.IGNORECASE) for name in exclude
                )
            ]
        return [str(path) for path in Path(root).rglob("*.sql")]
    return [str(path) for path in paths]


@lru_cache(maxsize=None)
def sql_format(path):
    """Convert SQL statement by sqlparse format.

    Args:
        path (str): Path to a SQL file.

    Returns:
        sql (str): Formatted SQL statement.

    """
    with Path(path).open("r") as sql_file:
        sql = sql_file.read()
    sql = sqlparse.format(
        sql,
        strip_comments=True,
        strip_whitespace=True,
        keyword_case="upper",
        encoding="utf8",
    ).replace("\n", " ")

    return sql


def get_schema_name(sql):
    """Get schema object.

    Args:
        sql (str): A SQL statement.

    Returns:
        schema (obj): sqlparse Identifier.

    """
    # get a tuple of token instances and grab the Statement object
    parser = cached_parse(sql)[0]
    # get a list of tokens attribute of the object
    tlist = parser.tokens
    # filter tokens by None type
    ftokens = [t for t in tlist if t.ttype is None]
    # get schema definition depending on type from nested/non-nested identifier list
    try:
        schema = (
            list(chain(ftokens[0]))[0]
            if isinstance(ftokens[0], IdentifierList)
            else ftokens[0]
        )
        return schema
    # handler for snake case variable if list index out of range
    except IndexError as err:
        return err


def sql_filter(sql, *types):
    """Get filtered SQL statements.

    Args:
        sql (str): A string containing one or more SQL statements.
        *types: A list of SQL types to be filtered [DDL, DML, CTE].

    Returns:
        fstmts (:list:`str`): Filtered list of SQL statements.

    """
    stmts = cached_parse(sql)
    fstmts = []

    for stmt in stmts:
        if not stmt.is_group:
            return False
        for token in stmt.tokens:
            if token.ttype in types:
                fstmts.append(str(stmt))
    return fstmts


def get_fobj(path, schema=False):
    """Get a file object based on path.

    Args:
        path (str): A path to a SQL file.
        schema (bool): Default False,
                       True will get a schema name from a SQL file path.

    Returns:
        (str): A SQL filename if schema=False, otherwise schema name.

    """
    return PurePath(path).parts[1] if schema else PurePath(path).stem.split(".")[0]


def check_stmt(stmt, cmds, exclude=False, exception=None):
    """Check whether SQL statement contains command or not.

    Args:
        stmt (str): A SQL statement.
        cmds (:list:`str`): A list of SQL commands.
        exclude (bool): False (default) check that command is in SQL statement,
                        True check that command is not in SQL statement.
        exception (list): A list of exceptional cmds.

    Returns:
        (bool): True if exclude=False and command was found inside SQL statement,
                True if exclude=False and exception=['SOME', 'CMD'] and command was found
                inside SQL statement and not in exception cmds list.
                True if exclude=True and all commands were not found in SQL
                statement (check all commands except in cmds), False otherwise.

    """
    if exclude:
        return all(cmd not in stmt for cmd in cmds)
    if exception:
        return any(
            cmd in stmt and set(stmt.split()).isdisjoint(set(exception)) for cmd in cmds
        )
    return any(cmd in stmt for cmd in cmds)


def parse_sql(path, *types):
    """Get SQL, statements and schema object.

    Args:
        path (str): A path to the SQL file.
        *types: A list of SQL types to be filtered [DDL, DML, CTE].

    Returns:
        sql (str): Formatted SQL statement.
        fstmts (:list:`str`): Filtered list of SQL statements.
        schema (obj): A schema object.

    """
    sql = sql_format(path)
    fstmts = sql_filter(sql, *types)
    schema = get_schema_name(sql)
    return sql, fstmts, schema


def get_run_set(bdir, runs):
    """Get a runset of runner file path and SQL file names in the same directory.

    Args:
        bdir (str): A base directory where start recursive searching.
        runs (str): A name of runner script.

    Returns:
        run_set (tuple): A set of `runs` paths and SQL file names in folder.
        ('/path/to/run.sh', [1.SQL, 2.SQL, ..n], ..).

    """
    path = Path(bdir)
    dirs = [unit for unit in path.iterdir() if unit.is_dir()]
    run_set = [
        (
            "".join(list(map(str, (Path(dir).rglob(runs))))),
            list(map(lambda sqlfile: sqlfile.name, (Path(dir).rglob("*.sql")))),
        )
        for dir in dirs
    ]

    return run_set


def parse_run_set(rset, ptrn_exarun, ptrn_valid, ptrn_sql):
    """
    Parse given runset to get collections of valid SQL `exa_run` cmds, SQL file
    names in directory, path to runner and wrong `exa_run` cmds in runner.

    Args:
        rset (tuple): A set of runner path and SQL file names in folder.
        ptrn_exarun (str): Regexp pattern with prefix `r` for
                           searching all uncommented `exa_run` cmds in file.
        ptrn_valid (str): Regexp pattern with prefix `r` to
                          validate `exa_run` cmd.
        ptrn_sql (str): Regexp pattern with prefix `r` to get SQL
                        name from valid `exa_run` cmd.

    Returns:
        valid_sqls (list): A list of valid SQL names in runner file.
        sqlsl (list): A list of SQL file names in directory.
        runf (str): A path to runner file.
        wrong_runs (list): A list of not valid `exa_run` cmds in runner.

    """
    valid_sqls = []
    wrong_runs = []
    sqlsl = None
    runf = None
    for runf, sqlsl in rset:
        exa_runs = re.findall(ptrn_exarun, Path(runf).read_text(), re.I | re.M)
        for exa_run in exa_runs:
            if re.match(ptrn_valid, exa_run):
                valid_sqls.append(re.search(ptrn_sql, exa_run).group(1))
            else:
                wrong_runs.append(exa_run)
    return valid_sqls, sqlsl, runf, wrong_runs


def assert_sql_contains_only(path, cmds, exclude=False):
    """
    Reads a SQL file under given path and checks if each command contains required command.

    Args:
        path (str): Path to the SQL file to be parsed.
        cmds (list): List of commands to check for.
        exclude (bool): Optional flag. When true, checks if each command
                        is not present in any of the statements.

    Returns:
        Nothing.

    """
    _, stmts, _ = parse_sql(path, DDL)

    for cmd in cmds:
        for stmt in stmts:
            check = check_stmt(stmt, [cmd], exclude)
            if exclude:
                assert check, f"{path} should not contain {cmd} statement(s)!"
            else:
                assert check, f"{path} should contain only {cmd} statement(s)!"
