PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS data_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    node_id TEXT NOT NULL UNIQUE,
    data_type TEXT NOT NULL,
    unit TEXT,
    component TEXT,
    category TEXT,
    source_block TEXT,
    poll_group TEXT NOT NULL,
    poll_interval_s REAL NOT NULL DEFAULT 1.0,

    is_required INTEGER NOT NULL DEFAULT 1,
    is_context INTEGER NOT NULL DEFAULT 0,
    use_in_fsm INTEGER NOT NULL DEFAULT 0,
    use_in_api INTEGER NOT NULL DEFAULT 1,
    use_in_anomaly INTEGER NOT NULL DEFAULT 1,

    validation_status TEXT NOT NULL DEFAULT 'unknown',
    validation_note TEXT
);

CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    received_at TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'OPC-UA',
    collector_status TEXT NOT NULL DEFAULT 'OK',
    aktueller_schritt INTEGER,
    fsm_state TEXT
);

CREATE TABLE IF NOT EXISTS measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id INTEGER NOT NULL,
    data_point_id INTEGER NOT NULL,

    timestamp TEXT NOT NULL,
    value_real REAL,
    value_int INTEGER,
    value_bool INTEGER,
    value_text TEXT,

    quality TEXT,
    source_timestamp TEXT,
    server_timestamp TEXT,

    FOREIGN KEY (snapshot_id) REFERENCES snapshots(id) ON DELETE CASCADE,
    FOREIGN KEY (data_point_id) REFERENCES data_points(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS process_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id INTEGER NOT NULL,
    aktueller_schritt INTEGER,
    fsm_state TEXT,
    previous_state TEXT,
    time_in_state_s REAL,
    transition_reason TEXT,
    created_at TEXT NOT NULL,

    FOREIGN KEY (snapshot_id) REFERENCES snapshots(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS alarms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id INTEGER,
    rule_id TEXT NOT NULL,
    code TEXT NOT NULL,
    severity TEXT NOT NULL,
    state TEXT,
    component TEXT,
    variable TEXT,
    value TEXT,
    threshold TEXT,
    message TEXT,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    created_at TEXT NOT NULL,
    cleared_at TEXT,

    FOREIGN KEY (snapshot_id) REFERENCES snapshots(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS system_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id INTEGER,
    created_at TEXT NOT NULL,
    level TEXT NOT NULL,
    event_type TEXT NOT NULL,
    message TEXT NOT NULL,

    FOREIGN KEY (snapshot_id) REFERENCES snapshots(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_measurements_snapshot
ON measurements(snapshot_id);

CREATE INDEX IF NOT EXISTS idx_measurements_data_point_time
ON measurements(data_point_id, timestamp);

CREATE INDEX IF NOT EXISTS idx_snapshots_received_at
ON snapshots(received_at);

CREATE INDEX IF NOT EXISTS idx_alarms_status
ON alarms(status);

CREATE VIEW IF NOT EXISTS v_latest_measurements AS
SELECT
    dp.name,
    dp.unit,
    dp.component,
    dp.category,
    dp.validation_status,
    m.timestamp,
    COALESCE(
        CAST(m.value_real AS TEXT),
        CAST(m.value_int AS TEXT),
        CAST(m.value_bool AS TEXT),
        m.value_text
    ) AS value,
    m.quality
FROM measurements m
JOIN data_points dp ON dp.id = m.data_point_id
JOIN (
    SELECT data_point_id, MAX(timestamp) AS latest_timestamp
    FROM measurements
    GROUP BY data_point_id
) latest
ON latest.data_point_id = m.data_point_id
AND latest.latest_timestamp = m.timestamp;