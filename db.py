import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "powerwise.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS household (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            household_name TEXT NOT NULL DEFAULT 'My Home',
            location TEXT NOT NULL DEFAULT '',
            state TEXT NOT NULL DEFAULT 'Selangor',
            provider TEXT NOT NULL DEFAULT 'TNB',
            household_size INTEGER NOT NULL DEFAULT 4,
            monthly_budget REAL NOT NULL DEFAULT 200.0,
            alert_threshold REAL NOT NULL DEFAULT 0.8,
            language TEXT NOT NULL DEFAULT 'en'
        );

        INSERT OR IGNORE INTO household (id) VALUES (1);

        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            serial_number TEXT UNIQUE NOT NULL,
            connected INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS energy_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            energy_in REAL NOT NULL,
            energy_out REAL NOT NULL DEFAULT 0.0,
            power REAL NOT NULL DEFAULT 0.0,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_readings_device_ts
            ON energy_readings(device_id, timestamp);

        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month TEXT NOT NULL,
            kwh_used REAL NOT NULL,
            amount REAL NOT NULL,
            input_method TEXT NOT NULL DEFAULT 'manual',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS appliances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            appliance_type TEXT NOT NULL,
            power_watts REAL NOT NULL,
            hours_per_day REAL NOT NULL DEFAULT 4.0,
            energy_rating TEXT NOT NULL DEFAULT '',
            purchase_year INTEGER,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    conn.close()


# ── Household Profile ─────────────────────────────────────────────────────────

def get_household() -> dict:
    conn = get_connection()
    row = conn.execute("SELECT * FROM household WHERE id = 1").fetchone()
    conn.close()
    return dict(row)


def update_household(**kwargs):
    conn = get_connection()
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    conn.execute(f"UPDATE household SET {sets} WHERE id = 1", list(kwargs.values()))
    conn.commit()
    conn.close()


# ── Device CRUD ───────────────────────────────────────────────────────────────

def add_device(name: str, serial_number: str) -> int:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO devices (name, serial_number) VALUES (?, ?)",
        (name, serial_number),
    )
    conn.commit()
    device_id = cur.lastrowid
    conn.close()
    return device_id


def get_devices() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM devices ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_device(device_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM devices WHERE id = ?", (device_id,))
    conn.commit()
    conn.close()


def update_device_connection(device_id: int, connected: bool):
    conn = get_connection()
    conn.execute("UPDATE devices SET connected = ? WHERE id = ?", (int(connected), device_id))
    conn.commit()
    conn.close()


# ── Energy Readings ───────────────────────────────────────────────────────────

def add_reading(device_id: int, timestamp: str, energy_in: float, energy_out: float, power: float):
    conn = get_connection()
    conn.execute(
        "INSERT INTO energy_readings (device_id, timestamp, energy_in, energy_out, power) VALUES (?, ?, ?, ?, ?)",
        (device_id, timestamp, energy_in, energy_out, power),
    )
    conn.commit()
    conn.close()


def add_readings_bulk(readings: list[tuple]):
    conn = get_connection()
    conn.executemany(
        "INSERT INTO energy_readings (device_id, timestamp, energy_in, energy_out, power) VALUES (?, ?, ?, ?, ?)",
        readings,
    )
    conn.commit()
    conn.close()


def get_readings(device_id: int, start: str | None = None, end: str | None = None) -> list[dict]:
    conn = get_connection()
    query = "SELECT * FROM energy_readings WHERE device_id = ?"
    params: list = [device_id]
    if start:
        query += " AND timestamp >= ?"
        params.append(start)
    if end:
        query += " AND timestamp <= ?"
        params.append(end)
    query += " ORDER BY timestamp ASC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_readings(start: str | None = None, end: str | None = None) -> list[dict]:
    conn = get_connection()
    query = "SELECT er.*, d.name as device_name FROM energy_readings er JOIN devices d ON er.device_id = d.id"
    params: list = []
    conditions = []
    if start:
        conditions.append("er.timestamp >= ?")
        params.append(start)
    if end:
        conditions.append("er.timestamp <= ?")
        params.append(end)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY er.timestamp ASC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_latest_reading(device_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM energy_readings WHERE device_id = ? ORDER BY timestamp DESC LIMIT 1",
        (device_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_device_count() -> int:
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) as cnt FROM devices").fetchone()
    conn.close()
    return row["cnt"]


def get_reading_count() -> int:
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) as cnt FROM energy_readings").fetchone()
    conn.close()
    return row["cnt"]


# ── Bills ─────────────────────────────────────────────────────────────────────

def add_bill(month: str, kwh_used: float, amount: float, input_method: str = "manual") -> int:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO bills (month, kwh_used, amount, input_method) VALUES (?, ?, ?, ?)",
        (month, kwh_used, amount, input_method),
    )
    conn.commit()
    bill_id = cur.lastrowid
    conn.close()
    return bill_id


def get_bills() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM bills ORDER BY month DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_latest_bill() -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM bills ORDER BY month DESC LIMIT 1").fetchone()
    conn.close()
    return dict(row) if row else None


# ── Appliances ────────────────────────────────────────────────────────────────

def add_appliance(name: str, appliance_type: str, power_watts: float, hours_per_day: float, energy_rating: str = "", purchase_year: int | None = None) -> int:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO appliances (name, appliance_type, power_watts, hours_per_day, energy_rating, purchase_year) VALUES (?, ?, ?, ?, ?, ?)",
        (name, appliance_type, power_watts, hours_per_day, energy_rating, purchase_year),
    )
    conn.commit()
    appliance_id = cur.lastrowid
    conn.close()
    return appliance_id


def get_appliances() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM appliances ORDER BY power_watts DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_appliance(appliance_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM appliances WHERE id = ?", (appliance_id,))
    conn.commit()
    conn.close()
