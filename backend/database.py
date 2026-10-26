import sqlite3
import os

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "coffees.db")
DB_PATH = os.environ.get("TEST_DB") or os.environ.get("COFFEE_DB_PATH") or DEFAULT_DB_PATH

INITIAL_COFFEES = [
    (
        "Espresso",
        "A bold, concentrated shot of pure coffee magic. Intense flavor extracted under high pressure.",
        "https://images.unsplash.com/photo-1510591509098-f4fdc6d0ff04?w=600&q=80",
    ),
    (
        "Cappuccino",
        "Velvety steamed milk foam layered over rich espresso. The perfect balance of bold and creamy.",
        "https://images.unsplash.com/photo-1572442388796-11668a67e53d?w=600&q=80",
    ),
    (
        "Latte",
        "Silky steamed milk poured over espresso, creating a smooth, comforting coffee experience.",
        "https://images.unsplash.com/photo-1561882468-9110d70d0578?w=600&q=80",
    ),
    (
        "Americano",
        "Espresso diluted with hot water for a long, clean, and approachable coffee with depth.",
        "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=600&q=80",
    ),
    (
        "Mocha",
        "A decadent blend of rich espresso, steamed milk, and luscious chocolate. Dessert in a cup.",
        "https://images.unsplash.com/photo-1578314675249-a6910f80cc4e?w=600&q=80",
    ),
    (
        "Flat White",
        "Ristretto shots with a micro-foam milk texture. Strong, smooth, and distinctly Australian.",
        "https://images.unsplash.com/photo-1577968897966-3d4325b36b61?w=600&q=80",
    ),
]


def get_connection():
    """Get a database connection with row factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database: create table and seed default coffees."""
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS coffees (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL UNIQUE,
                description TEXT    NOT NULL,
                image_url   TEXT    NOT NULL,
                vote_count  INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.commit()

        # Insert defaults only if they don't already exist
        for name, description, image_url in INITIAL_COFFEES:
            conn.execute(
                """
                INSERT OR IGNORE INTO coffees (name, description, image_url, vote_count)
                VALUES (?, ?, ?, 0)
                """,
                (name, description, image_url),
            )
        conn.commit()
    finally:
        conn.close()


def get_all_coffees():
    """Return all coffees ordered by vote_count descending."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, name, description, image_url, vote_count FROM coffees ORDER BY vote_count DESC"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def vote_for_coffee(coffee_id: int):
    """
    Atomically increment vote_count for the given coffee.
    Returns the updated row dict, or None if the coffee doesn't exist.
    """
    conn = get_connection()
    try:
        with conn:  # transaction context manager – auto-commit or rollback
            cursor = conn.execute(
                "UPDATE coffees SET vote_count = vote_count + 1 WHERE id = ?",
                (coffee_id,),
            )
            if cursor.rowcount == 0:
                return None  # coffee not found

            row = conn.execute(
                "SELECT id, name, description, image_url, vote_count FROM coffees WHERE id = ?",
                (coffee_id,),
            ).fetchone()
            return dict(row)
    finally:
        conn.close()
