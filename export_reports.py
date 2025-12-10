"""Run reporting queries on ecom.db and write outputs to CSV files."""

from __future__ import annotations

import csv
import sqlite3
from contextlib import closing
from pathlib import Path


def fetch_rows(conn: sqlite3.Connection, query: str) -> tuple[list[str], list[tuple]]:
    cur = conn.execute(query)
    headers = [col[0] for col in cur.description]
    rows = cur.fetchall()
    return headers, rows


def write_csv(path: Path, headers: list[str], rows: list[tuple]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


def main(db_path: str = "ecom.db", output_dir: str = "reports") -> None:
    queries = {
        "top_users_by_spending.csv": """
            SELECT
                u.user_id,
                u.name,
                u.email,
                SUM(o.total_amount) AS total_spent,
                COUNT(DISTINCT o.order_id) AS orders_count
            FROM users u
            JOIN orders o ON o.user_id = u.user_id
            GROUP BY u.user_id, u.name, u.email
            ORDER BY total_spent DESC
            LIMIT 10;
        """,
        "top_products_by_revenue.csv": """
            SELECT
                p.product_id,
                p.name,
                p.category,
                SUM(oi.line_total) AS revenue,
                SUM(oi.quantity) AS units_sold,
                COUNT(DISTINCT oi.order_id) AS orders_count
            FROM products p
            JOIN order_items oi ON oi.product_id = p.product_id
            GROUP BY p.product_id, p.name, p.category
            ORDER BY revenue DESC
            LIMIT 10;
        """,
        "avg_rating_per_product.csv": """
            SELECT
                p.product_id,
                p.name,
                p.category,
                ROUND(AVG(r.rating), 2) AS avg_rating,
                COUNT(r.review_id) AS review_count
            FROM products p
            JOIN reviews r ON r.product_id = p.product_id
            GROUP BY p.product_id, p.name, p.category
            ORDER BY avg_rating DESC, review_count DESC;
        """,
        "country_level_revenue.csv": """
            SELECT
                u.country,
                SUM(o.total_amount) AS revenue,
                COUNT(DISTINCT o.order_id) AS orders_count,
                COUNT(DISTINCT u.user_id) AS users_count
            FROM users u
            JOIN orders o ON o.user_id = u.user_id
            GROUP BY u.country
            ORDER BY revenue DESC;
        """,
    }

    db_file = Path(db_path)
    if not db_file.exists():
        raise FileNotFoundError(f"Database not found: {db_file.resolve()}")

    out_dir = Path(output_dir)

    with closing(sqlite3.connect(db_file)) as conn:
        for filename, query in queries.items():
            headers, rows = fetch_rows(conn, query)
            write_csv(out_dir / filename, headers, rows)
            print(f"Wrote {filename} with {len(rows)} rows")

    print(f"Reports written to {out_dir.resolve()}")


if __name__ == "__main__":
    main()

