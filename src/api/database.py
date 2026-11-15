
import sqlite3
from pathlib import Path

# Project and database paths
PROJECT_PATH = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_PATH / "data" / "opsmind.db"


def get_connection():
    """Create and return a SQLite database connection."""

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=30,
        check_same_thread=False
    )

    connection.execute("PRAGMA busy_timeout = 30000")
    connection.row_factory = sqlite3.Row

    return connection


def create_tables():
    """Create ticket and log history tables if they do not exist."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ticket_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            predicted_category TEXT NOT NULL,
            confidence REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS log_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            severity TEXT NOT NULL,
            component TEXT NOT NULL,
            source TEXT NOT NULL,
            prediction TEXT NOT NULL,
            anomaly_probability REAL NOT NULL,
            normal_probability REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def save_ticket(description, predicted_category, confidence):
    """Save a classified ticket to the database."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO ticket_history
        (description, predicted_category, confidence)
        VALUES (?, ?, ?)
    """, (
        description,
        predicted_category,
        confidence
    ))

    connection.commit()
    connection.close()


def save_log(log_record, result):
    """Save a log analysis result to the database."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO log_history
        (
            message,
            severity,
            component,
            source,
            prediction,
            anomaly_probability,
            normal_probability
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        log_record["message"],
        log_record["severity"],
        log_record["component"],
        log_record["source"],
        result["prediction"],
        result["anomaly_probability"],
        result["normal_probability"]
    ))

    connection.commit()
    connection.close()


def get_ticket_history(limit=20):
    """Retrieve recent ticket history."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM ticket_history
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    records = [dict(row) for row in cursor.fetchall()]

    connection.close()

    return records


def get_log_history(limit=20):
    """Retrieve recent log analysis history."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM log_history
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    records = [dict(row) for row in cursor.fetchall()]

    connection.close()

    return records
