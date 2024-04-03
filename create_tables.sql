-- Create tables for bikeparkingdb
--
-- Reminder: set PRAGMA FOREIGN KEYS = ON; at session starts

CREATE TABLE DAY (
    id INTEGER PRIMARY KEY,

    org_code TEXT NOT NULL,
    site_code TEXT DEFAULT 'unspecified',
    date DATE
        NOT NULL
        CHECK(
            date LIKE '____-__-__'
            AND date BETWEEN '2000-01-01' AND '2100-01-01'
        ),

    time_open TEXT
        CHECK (
            time_open LIKE "__:__"
            AND time_open BETWEEN '00:00' AND '24:00'
        ),
    time_closed TEXT
        CHECK (
            time_closed LIKE "__:__"
            AND time_closed BETWEEN '00:00' AND '24:00'
        ),
    bikes_regular INTEGER,
    bikes_oversize INTEGER,
    bikes_total INTEGER,
    -- bikes_registered is supplied by the organization
    bikes_registered INTEGER,
    -- weather statistics are looked up online from government sources
    max_temperature FLOAT,
    precipitation FLOAT,
    time_dusk TEXT
        CHECK (
            time_open LIKE "__:__"
            AND time_open BETWEEN '00:00' AND '24:00'
        ),

    UNIQUE ( date,org_code,site_code)
);
CREATE INDEX day_date_idx on day (date);
CREATE INDEX day_org_code_idx on day (org_code);
CREATE INDEX day_site_code_idx on day (site_code);



CREATE TABLE VISIT (
    id INTEGER PRIMARY KEY,
    day_id INTEGER,
    time_in TEXT
        NOT NULL
        CHECK (
            time_in LIKE "__:__"
            AND time_in BETWEEN '00:00' AND '24:00'
        ),
    duration INTEGER,
    bike_type TEXT
        CHECK (bike_type IN ('R', 'O')),
    bike_id TEXT,
    FOREIGN KEY (day_id) REFERENCES DAY (id) ON DELETE CASCADE
);

CREATE TABLE BLOCK (
    id INTEGER PRIMARY KEY,
    day_id INTEGER,
    time_start TEXT
        NOT NULL
        CHECK(
            time_start LIKE "__:__"
            AND time_start BETWEEN '00:00' AND '24:00'
        ),
    regular_at_start INTEGER,
    oversize_at_start INTEGER,
    oversize_at_end INTEGER,
    bikes_at_start INTEGER,
    bikes_at_end INTEGER,
    most_full INTEGER,
    time_most_full TEXT
        CHECK(
            time_most_full LIKE "__:__"
            AND time_most_full BETWEEN '00:00' AND '24:00'
        ),
    FOREIGN KEY (day_id) REFERENCES DAY (id) ON DELETE CASCADE
);

-- Information about the most recent successful data load
CREATE TABLE DATALOADS (
    id INTEGER PRIMARY KEY,
    day_id INTEGER,
    datafile_name TEXT,
    datafile_fingerprint TEXT,
    datafile_timestamp TEXT,
    load_timestamp TEXT,
    FOREIGN KEY (day_id) REFERENCES DAY (id) ON DELETE CASCADE
)