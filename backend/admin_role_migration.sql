-- Run once on an existing database created before the admin role was added.
ALTER TABLE mba_sumbagut.telegram_district_role
    DROP CONSTRAINT IF EXISTS chk_telegram_district_role_role;

ALTER TABLE mba_sumbagut.telegram_district_role
    ADD CONSTRAINT chk_telegram_district_role_role
    CHECK (role IN ('engineer', 'manager', 'admin'));
