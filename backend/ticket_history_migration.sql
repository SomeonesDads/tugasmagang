-- Indexes used by the read-only ticket history filters and lifecycle sorting.
CREATE INDEX IF NOT EXISTS idx_ticket_history_created_date
    ON mba_sumbagut.ticket (created_date);
CREATE INDEX IF NOT EXISTS idx_ticket_history_site_id
    ON mba_sumbagut.ticket (site_id);
CREATE INDEX IF NOT EXISTS idx_ticket_history_district
    ON mba_sumbagut.ticket (district_operation_do);
CREATE INDEX IF NOT EXISTS idx_ticket_history_rca_submitted_at
    ON mba_sumbagut.ticket_rca (submitted_at);
CREATE INDEX IF NOT EXISTS idx_ticket_history_service_end_day
    ON mba_sumbagut.ticket_service (end_day);
