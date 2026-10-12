CREATE TABLE IF NOT EXISTS config (
    key TEXT PRIMARY KEY ,
    value TEXT
);
CREATE TABLE IF NOT EXISTS linkedin (
    profile_id TEXT PRIMARY KEY ,
    profile TEXT NOT NULL CHECK ( json_valid(profile) )
);
