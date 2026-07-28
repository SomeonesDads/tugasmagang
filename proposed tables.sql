-- district & engineer roster (yours to maintain, not derived from sri_zp_daily)
CREATE TABLE district (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE field_engineer (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    telegram_username VARCHAR(100),
    name VARCHAR(200) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- junction, since a district can have 1-2 engineers
CREATE TABLE district_engineer (
    district_id INT REFERENCES district(id),
    engineer_id BIGINT REFERENCES field_engineer(id),
    PRIMARY KEY (district_id, engineer_id)
);

-- your own site->district mapping, since site_id has no real FK to hang this off
CREATE TABLE site_district_map (
    site_id VARCHAR(10) PRIMARY KEY,
    district_id INT REFERENCES district(id)
);
sql
-- core ticket
CREATE TABLE ticket (
    id BIGSERIAL PRIMARY KEY,
    enodeb_id INT4 NOT NULL,
    cell_id INT4 NOT NULL,
    site_id VARCHAR(10) NOT NULL,       -- intentionally not FK'd, matches source data
    district_id INT REFERENCES district(id),
    status VARCHAR(10) NOT NULL DEFAULT 'RCA',   -- RCA | SERVICE | CLOSED
    created_day DATE NOT NULL,
    closed_day DATE
);
CREATE INDEX idx_ticket_open_lookup ON ticket (enodeb_id, cell_id, site_id) WHERE status <> 'CLOSED';

-- awaiting engineer input
CREATE TABLE ticket_rca (
    ticket_id BIGINT PRIMARY KEY REFERENCES ticket(id),
    start_day DATE NOT NULL,
    end_day DATE,
    rca TEXT,           -- placeholder — will redefine once you send the actual taxonomy
    rca_detail TEXT
);

-- waiting for the feed to stop
CREATE TABLE ticket_service (
    ticket_id BIGINT PRIMARY KEY REFERENCES ticket(id),
    start_day DATE NOT NULL,
    end_day DATE
);