"""Load generated CSVs into a SQLite database named ecom.db."""

from __future__ import annotations

import csv
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Iterable


def drop_and_create_tables(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.executescript(
        """
        DROP TABLE IF EXISTS order_items;
        DROP TABLE IF EXISTS reviews;
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS users;

        CREATE TABLE users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            city TEXT,
            country TEXT,
            signup_date TEXT
        );

        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            price REAL,
            currency TEXT,
            stock_qty INTEGER,
            created_at TEXT
        );

        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            order_date TEXT,
            status TEXT,
            total_amount REAL
        );

        CREATE TABLE order_items (
            order_item_id INTEGER PRIMARY KEY,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            unit_price REAL,
            line_total REAL
        );

        CREATE TABLE reviews (
            review_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            product_id INTEGER,
            rating INTEGER,
            review_date TEXT,
            review_text TEXT
        );
        """
    )
    conn.commit()


def load_csv(conn: sqlite3.Connection, csv_path: Path, table: str, columns: list[str]) -> int:
    if not csv_path.exists():
        return 0

    placeholders = ",".join(["?"] * len(columns))
    insert_sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows: Iterable[tuple] = (tuple(row[col] for col in columns) for row in reader)
        conn.executemany(insert_sql, rows)
    conn.commit()
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def main(db_path: str = "ecom.db", data_dir: str = "data") -> None:
    data_path = Path(data_dir)
    if not data_path.exists():
        raise FileNotFoundError(f"Data directory not found: {data_path.resolve()}")

    csv_files = {
        "users": (data_path / "users.csv", ["user_id", "name", "email", "phone", "address", "city", "country", "signup_date"]),
        "products": (data_path / "products.csv", ["product_id", "name", "category", "price", "currency", "stock_qty", "created_at"]),
        "orders": (data_path / "orders.csv", ["order_id", "user_id", "order_date", "status", "total_amount"]),
        "order_items": (data_path / "order_items.csv", ["order_item_id", "order_id", "product_id", "quantity", "unit_price", "line_total"]),
        "reviews": (data_path / "reviews.csv", ["review_id", "user_id", "product_id", "rating", "review_date", "review_text"]),
    }

    with closing(sqlite3.connect(db_path)) as conn:
        drop_and_create_tables(conn)

        counts = {}
        for table, (path, cols) in csv_files.items():
            count = load_csv(conn, path, table, cols)
            counts[table] = count

    print(f"Database written to {Path(db_path).resolve()}")
    for table, count in counts.items():
        print(f"{table}: {count} rows")


if __name__ == "__main__":
    main()

