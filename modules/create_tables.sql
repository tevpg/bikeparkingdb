-- Create tables for bikeparkingdb
--
-- Reminder: set PRAGMA FOREIGN KEYS = ON; at session starts

-- There would be a 1:1 corrrespondence between 'id' and 'handle' values.
-- 'id' column is useful in code; 'handle' is useful for URLs and things
-- that might be helpful for maintenance and urL parameters etc

-- Note to self: comments at end of lines are retained in the schema definition
-- so using them keeps them visible in the '.sch' command in sqlite3

CREATE TABLE ORG (
    id INTEGER PRIMARY KEY,
    org_handle TEXT NOT NULL,   -- shortform text form of org
    org_name TEXT,  -- optional(?) descriptive name of org
    can_view_orgs TEXT,    -- list of org_handles whose data this org can see
    UNIQUE (org_handle)
);

-- A site is an arbitrary name of a location or event an org manages.
-- It affects aggregations of an org's data but is not tied to authorization
CREATE TABLE ORGSITE ( -- arbitrary sites used by an org. Not tied to authz.
    id integer PRIMARY KEY,
    org_id INTEGER NOT NULL,
    site_handle TEXT DEFAULT 'unspecified', -- human-handy reference to the site
    site_name TEXT, -- optional long name of the site
    FOREIGN KEY (org_id) REFERENCES ORG (id),
    UNIQUE (org_id, site_handle)
);


CREATE TABLE DAY (  -- Summary data about one org at one site on one day
    id INTEGER PRIMARY KEY,
    org_id INTEGER,
    site_id INTEGER,

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
    max_temperature FLOAT, -- to be looked up online, can be null
    precipitation FLOAT, -- to be looked up online, can be null
    time_dusk TEXT -- to be looked up online, can be null
        CHECK (
            time_open LIKE "__:__"
            AND time_open BETWEEN '00:00' AND '24:00'
        ),

    FOREIGN KEY (org_id) REFERENCES ORG (id),
    FOREIGN KEY (site_id) REFERENCES ORGSITE (id),
    UNIQUE ( date,org_id,site_id)
);
CREATE INDEX day_date_idx on day (date);
CREATE INDEX day_org_id_idx on day (org_id);
CREATE INDEX day_site_id_idx on day (site_id);

CREATE TABLE VISIT ( -- one bike visit for one org/site/date
    id INTEGER PRIMARY KEY,
    day_id INTEGER,
    time_in TEXT --
        NOT NULL
        CHECK (
            time_in LIKE "__:__"
            AND time_in BETWEEN '00:00' AND '24:00'
        ),
    duration INTEGER,
    bike_type TEXT
        CHECK (bike_type IN ('R', 'O')),
    bike_id TEXT, -- optional str to identify the bike (eg a tag)
    FOREIGN KEY (day_id) REFERENCES DAY (id) ON DELETE CASCADE
);

CREATE TABLE BLOCK ( -- activity in a given half hour for an org/site/date
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
CREATE TABLE DATALOADS ( -- info about most recent successful data loads
    id INTEGER PRIMARY KEY,
    day_id INTEGER,
    datafile_name TEXT, -- absolute path to file from which data loaded
    datafile_fingerprint TEXT, -- fingerprint (eg md5) of the file
    datafile_timestamp TEXT, -- timestamp of the file
    load_timestamp TEXT,    -- time at which the file was loaded
    FOREIGN KEY (day_id) REFERENCES DAY (id) ON DELETE CASCADE
);