CREATE TABLE IF NOT EXISTS DEV_STATS.AD_USER_DETAILS(
    "CN" VARCHAR(150) UTF8, 
    "GIVEN_NAME" VARCHAR(150) UTF8, 
    "EMPLOYEE_ID" VARCHAR(10) UTF8, 
    "SAMACCOUNTNAME" VARCHAR(10) UTF8, 
    "MAIL" VARCHAR(200) UTF8
);
COMMENT ON TABLE DEV_STATS.AD_USER_DETAILS is '';
