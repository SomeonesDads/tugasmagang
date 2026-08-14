-- Supporting indexes for chronological ticket backfills.
-- Run once against an existing database before a large replay.

CREATE INDEX IF NOT EXISTS idx_sri_zp_daily_backfill_lookup
    ON mba_sumbagut.sri_zp_daily ("date", enodeb_id, cell_id, site_id);

CREATE INDEX IF NOT EXISTS idx_sri_zt_daily_backfill_lookup
    ON mba_sumbagut.sri_zt_daily ("date", lac, ci, site_id);

CREATE INDEX IF NOT EXISTS idx_ticket_zp_identity
    ON mba_sumbagut.ticket (ticket_type, enodeb_id, cell_id, site_id);

CREATE INDEX IF NOT EXISTS idx_ticket_zt_identity
    ON mba_sumbagut.ticket (ticket_type, lac, ci, site_id);

CREATE INDEX IF NOT EXISTS idx_ticket_service_ticket_open
    ON mba_sumbagut.ticket_service (ticket_id)
    WHERE end_day IS NULL;
