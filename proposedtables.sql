-- Tables:
--   ticket                — base entity (ZP uses enodeb_id+cell_id, ZT uses lac+ci)
--   ticket_rca            — IS-A child; created immediately, filled by engineers
--   ticket_service        — IS-A child; inserted once ticket_rca.end_day is set
--
--   Tracking (refreshed daily by pipeline):
--      tracking_summary      — district-level aggregate metrics
--      tracking_detail       — district + RCA-category breakdown
--      tracking_summary_site — site-level aggregate metrics
--      tracking_detail_site  — site + RCA-category breakdown

-- DROP TABLE mba_sumbagut.ticket_service;
-- DROP TABLE mba_sumbagut.ticket_rca;
-- DROP TABLE mba_sumbagut.ticket;
-- DROP SEQUENCE mba_sumbagut.ticket_id_seq;


-- Sequence 

CREATE SEQUENCE mba_sumbagut.ticket_id_seq
    INCREMENT BY 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    START 1
    CACHE 1
    NO CYCLE;


--  mba_sumbagut.ticket 
--
-- Base ticket. One row per unique anomalous cell per day it first appears.
--
-- ZP rows carry (enodeb_id, cell_id) — cell_id/enodeb_id from sri_zp_daily.
-- ZT rows carry (lac, ci)            — from sri_zt_daily, which has no enodeb.
--
-- district_operation_do is denormalized from site_reference at creation time
-- so routing is self-contained without a cross-pipeline_run_id join later.
--
-- aging: for ZP, copied directly from sri_zp_daily.aging.
--        for ZT, computed as consecutive-day count (done in pipeline).

CREATE TABLE mba_sumbagut.ticket (
    ticket_id               bigint          NOT NULL DEFAULT nextval('mba_sumbagut.ticket_id_seq'),
    ticket_type             varchar(2)      NOT NULL,

    -- ZP identifiers (NULL for ZT rows)
    enodeb_id               int4            NULL,
    cell_id                 int4            NULL,

    -- ZT identifiers (NULL for ZP rows)
    lac                     int4            NULL,
    ci                      int4            NULL,

    -- Common
    site_id                 varchar(10)     NOT NULL,
    district_operation_do   varchar(100)    NULL,
    created_date            date            NOT NULL,   -- feed date that triggered creation
    aging                   int4            NOT NULL DEFAULT 1,
    created_at              timestamptz     NOT NULL DEFAULT now(),

    CONSTRAINT ticket_pkey PRIMARY KEY (ticket_id),

    CONSTRAINT chk_ticket_type CHECK (
        ticket_type IN ('ZP', 'ZT')
    ),
    -- ZP must always have both cell identifiers
    CONSTRAINT chk_ticket_zp_ids CHECK (
        ticket_type <> 'ZP' OR (enodeb_id IS NOT NULL AND cell_id IS NOT NULL)
    ),
    -- ZT must always have both legacy identifiers
    CONSTRAINT chk_ticket_zt_ids CHECK (
        ticket_type <> 'ZT' OR (lac IS NOT NULL AND ci IS NOT NULL)
    )
);

-- One ticket per (enodeb_id, cell_id, site_id) per day for ZP
CREATE UNIQUE INDEX uq_ticket_zp
    ON mba_sumbagut.ticket (enodeb_id, cell_id, site_id, created_date)
    WHERE ticket_type = 'ZP';

-- One ticket per (lac, ci, site_id) per day for ZT
CREATE UNIQUE INDEX uq_ticket_zt
    ON mba_sumbagut.ticket (lac, ci, site_id, created_date)
    WHERE ticket_type = 'ZT';

CREATE INDEX idx_ticket_site_id     ON mba_sumbagut.ticket (site_id);
CREATE INDEX idx_ticket_district    ON mba_sumbagut.ticket (district_operation_do);
CREATE INDEX idx_ticket_created     ON mba_sumbagut.ticket (created_date DESC);
CREATE INDEX idx_ticket_type        ON mba_sumbagut.ticket (ticket_type);


--  mba_sumbagut.ticket_rca 
--
-- IS-A child of ticket. Inserted automatically when a ticket is created.
-- Engineers populate rca + rca_detail via bot/API.
-- Setting rca marks the analysis complete → end_day is set → ticket_service row
-- is inserted by the backend.
--
-- RCA values come from the official enum provided 2026-07-28.

CREATE TABLE mba_sumbagut.ticket_rca (
    ticket_id       bigint          NOT NULL,
    start_day       date            NOT NULL,
    end_day         date            NULL,       -- NULL until engineer submits RCA

    rca             varchar(50)     NULL,
    rca_detail      text            NULL,

    submitted_at    timestamptz     NULL,
    updated_at      timestamptz     NOT NULL DEFAULT now(),

    CONSTRAINT ticket_rca_pkey PRIMARY KEY (ticket_id),
    CONSTRAINT ticket_rca_fkey FOREIGN KEY (ticket_id)
        REFERENCES mba_sumbagut.ticket (ticket_id),

    CONSTRAINT chk_rca CHECK (rca IS NULL OR rca IN (
        'Software Problem',
        'Activity Project',
        'Hardware Problem',
        'Power Problem',
        'Transmition Problem',
        'Stolen',
        'Force Majure',
        'Comcase',
        'Sleeping Cell',
        'No Traffic/User',
        'Dismantled'
    )),

    CONSTRAINT chk_rca_detail CHECK (rca_detail IS NULL OR rca_detail IN (
        -- Software Problem
        'Configuration Problem',
        'Database',
        -- Activity Project
        'Cell Locked',
        'Activity Event',
        'Activity Upgrade',
        'Activity Downgrade',
        'Activity Blacksite',
        -- Hardware Problem
        'DAS Problem',
        'Hardware Hang, No Alarm',
        'Baseband Problem',
        'UMPT/UBBP Problem',
        'Antenna Problem',
        'Antenna Port Problem',
        'Flexible Jumper',
        'RRU Problem',
        'SFP Problem',
        'GPS Problem',
        'Optic Problem',
        -- Power Problem
        'Rectifier Problem',
        'Kabel Power Problem',
        'Genset Problem',
        'Pemadaman PLN',
        -- Transmition Problem
        'NPU Problem',
        'MMU Problem',
        'RAU Problem',
        'Metro-E Problem',
        'VLAN Problem',
        'Impact Simpul',
        'Fading',
        -- Stolen
        'stolen Baseband',
        'Stolen RRU',
        'Stolen BBU',
        'Stolen UBBP',
        'Stolen UMPT',
        'Stolen UBBP + UMPT',
        'Stolen Cable Power',
        -- Force Majure
        'Banjir',
        'Site Rubuh',
        'Perangkat Terbakar',
        -- Single-value RCAs (rca_detail mirrors rca)
        'Comcase',
        'Sleeping Cell',
        'No Traffic/User',
        'Dismantled'
    ))
);

-- Fast lookup for open RCA tickets (awaiting engineer input)
CREATE INDEX idx_ticket_rca_open ON mba_sumbagut.ticket_rca (ticket_id)
    WHERE end_day IS NULL;

-- Fast lookup for tickets awaiting service (RCA done, service not yet opened)
CREATE INDEX idx_ticket_rca_pending_svc ON mba_sumbagut.ticket_rca (end_day)
    WHERE end_day IS NOT NULL;


--  mba_sumbagut.ticket_service 
--
-- IS-A child of ticket. Inserted by backend when ticket_rca.end_day is set.
-- start_day = ticket_rca.end_day.
-- end_day is set by the daily pipeline when the problematic cell no longer
-- appears in sri_zp_daily / sri_zt_daily for that day.
-- Minimum service duration is 1 day (feed is daily, so resolution can only
-- be detected on the next pipeline run).

CREATE TABLE mba_sumbagut.ticket_service (
    ticket_id       bigint          NOT NULL,
    start_day       date            NOT NULL,   -- = ticket_rca.end_day
    end_day         date            NULL,       -- NULL until cell clears from feed

    updated_at      timestamptz     NOT NULL DEFAULT now(),

    CONSTRAINT ticket_service_pkey PRIMARY KEY (ticket_id),
    CONSTRAINT ticket_service_fkey FOREIGN KEY (ticket_id)
        REFERENCES mba_sumbagut.ticket (ticket_id)
);

-- Fast lookup for open service tickets (checked daily by pipeline)
CREATE INDEX idx_ticket_service_open ON mba_sumbagut.ticket_service (ticket_id)
    WHERE end_day IS NULL;


-- ============================================================
-- Tracking Tables
-- Refreshed at the end of every pipeline run (seed or daily).
-- All use UPSERT so they are safe to recompute from scratch.
--
-- Metrics:
--   count_problems        total tickets ever opened for this group
--   solved_rca            tickets where engineer submitted RCA
--   solved_service        tickets where problem fully cleared from feed
--   solved_rca_avg_time   avg days: ticket creation → RCA submitted (analysis time)
--   solved_service_avg_time avg days: service opened → service closed (service time)
-- ============================================================


--  mba_sumbagut.tracking_summary (district level) 
--
-- One row per district.  Gives management a quick view of how each district
-- is performing on ticket resolution.

CREATE TABLE mba_sumbagut.tracking_summary (
    district                varchar(100)    NOT NULL,
    count_problems          int4            NOT NULL DEFAULT 0,
    solved_rca              int4            NOT NULL DEFAULT 0,
    solved_service          int4            NOT NULL DEFAULT 0,
    solved_rca_avg_time     numeric(8,2)    NULL,
    solved_service_avg_time numeric(8,2)    NULL,
    updated_at              timestamptz     NOT NULL DEFAULT now(),
    CONSTRAINT tracking_summary_pkey PRIMARY KEY (district)
);


--  mba_sumbagut.tracking_detail (district + RCA category) 
--
-- One row per (district, rca).  Only tickets that have had an RCA submitted
-- appear here.  Enables per-cause drilldown within a district.

CREATE TABLE mba_sumbagut.tracking_detail (
    district                varchar(100)    NOT NULL,
    rca                     varchar(50)     NOT NULL,
    count_problems          int4            NOT NULL DEFAULT 0,
    solved_rca              int4            NOT NULL DEFAULT 0,
    solved_service          int4            NOT NULL DEFAULT 0,
    solved_rca_avg_time     numeric(8,2)    NULL,
    solved_service_avg_time numeric(8,2)    NULL,
    updated_at              timestamptz     NOT NULL DEFAULT now(),
    CONSTRAINT tracking_detail_pkey PRIMARY KEY (district, rca)
);

CREATE INDEX idx_tracking_detail_district ON mba_sumbagut.tracking_detail (district);


--  mba_sumbagut.tracking_summary_site (site level) 
--
-- One row per site_id.  Site-granularity version of tracking_summary,
-- matching the ER diagram.  Useful for surfacing problem sites to engineers.

CREATE TABLE mba_sumbagut.tracking_summary_site (
    site_id                 varchar(10)     NOT NULL,
    count_problems          int4            NOT NULL DEFAULT 0,
    solved_rca              int4            NOT NULL DEFAULT 0,
    solved_service          int4            NOT NULL DEFAULT 0,
    solved_rca_avg_time     numeric(8,2)    NULL,
    solved_service_avg_time numeric(8,2)    NULL,
    updated_at              timestamptz     NOT NULL DEFAULT now(),
    CONSTRAINT tracking_summary_site_pkey PRIMARY KEY (site_id)
);


--  mba_sumbagut.tracking_detail_site (site + RCA category) 
--
-- One row per (site_id, rca).  Site-granularity version of tracking_detail.
-- Useful for seeing which root causes repeat at a specific site.

CREATE TABLE mba_sumbagut.tracking_detail_site (
    site_id                 varchar(10)     NOT NULL,
    rca                     varchar(50)     NOT NULL,
    count_problems          int4            NOT NULL DEFAULT 0,
    solved_rca              int4            NOT NULL DEFAULT 0,
    solved_service          int4            NOT NULL DEFAULT 0,
    solved_rca_avg_time     numeric(8,2)    NULL,
    solved_service_avg_time numeric(8,2)    NULL,
    updated_at              timestamptz     NOT NULL DEFAULT now(),
    CONSTRAINT tracking_detail_site_pkey PRIMARY KEY (site_id, rca)
);

CREATE INDEX idx_tracking_detail_site_site ON mba_sumbagut.tracking_detail_site (site_id);
