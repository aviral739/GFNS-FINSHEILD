cursor.execute("""
CREATE TABLE IF NOT EXISTS bank_capital_adequacy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    institution TEXT,
    region TEXT,
    tier1_capital_ratio REAL,
    status TEXT,
    recorded_at TEXT
)
""")