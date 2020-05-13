CREATE
    OR REPLACE VIEW DEV_PROC.AD_MISSING_USERS AS SELECT
        NVL(
            ad.GIVEN_NAME,
            'Team'
        ) AS GIVAN_NAME,
        NVL(
            ad.MAIL,
            'ERROR'
        ) AS MAIL,
        a.SESSION_ID || '_' || '*' || 'GB.SQL' AS FILE_NAME,
        s.USER_NAME,
        LOWER( REGEXP_REPLACE( a.SQL_TEXT, '(?s).*\/\* ([A-z0-9]*)\,.*\*\/.*', '\1' )) AS LOGIN,
        a.SQL_TEXT
    FROM
        EXA_DBA_AUDIT_SQL AS a
    JOIN EXA_DBA_AUDIT_SESSIONS AS s ON
        a.SESSION_ID = s.SESSION_ID
    LEFT JOIN DEV_PROC.AD_USER_DETAILS AS ad ON
        LOWER( REGEXP_REPLACE( a.SQL_TEXT, '(?s).*\/\* ([A-z0-9]*)\,.*\*\/.*', '\1' ))= LOWER( ad.SAMACCOUNTNAME )
    WHERE
        s.USER_NAME LIKE '%MSTRUSER'
        AND a.TEMP_DB_RAM_PEAK / 1024 > 500
        AND a.COMMAND_CLASS = 'DQL'
        AND ad.GIVEN_NAME IS NULL
        AND a.SQL_TEXT REGEXP_LIKE '(?s).*\/\* ([A-z0-9]*)\,.*\*\/.*';
