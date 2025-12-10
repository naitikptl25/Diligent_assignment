"""Generate synthetic e-commerce CSVs (users, products, orders, order_items, reviews)."""

from __future__ import annotations

import csv
import random
from pathlib import Path

from faker import Faker


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    """Write dictionaries to CSV with headers."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def generate_users(fake: Faker, count: int) -> list[dict]:
    users = []
    for user_id in range(1, count + 1):
        profile = fake.simple_profile()
        users.append(
            {
                "user_id": user_id,
                "name": profile["name"],
                "email": profile["mail"],
                "phone": fake.phone_number(),
                "address": fake.street_address().replace("\n", ", "),
                "city": fake.city(),
                "country": fake.country(),
                "signup_date": fake.date_between(start_date="-2y", end_date="today"),
            }
        )
    return users


def generate_products(fake: Faker, count: int) -> list[dict]:
    categories = [
        "Electronics",
        "Home & Kitchen",
        "Books",
        "Fashion",
        "Sports",
        "Beauty",
        "Toys",
        "Groceries",
    ]
    products = []
    for product_id in range(1, count + 1):
        category = random.choice(categories)
        price = round(random.uniform(5, 500), 2)
        products.append(
            {
                "product_id": product_id,
                "name": f"{fake.color_name()} {fake.word().title()}",
                "category": category,
                "price": price,
                "currency": "USD",
                "stock_qty": random.randint(0, 500),
                "created_at": fake.date_between(start_date="-2y", end_date="-1d"),
            }
        )
    return products


def generate_orders(fake: Faker, users: list[dict], products: list[dict], count: int):
    statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
    orders = []
    order_items = []
    order_item_id = 1

    for order_id in range(1, count + 1):
        user = random.choice(users)
        order_date = fake.date_time_between(start_date="-18m", end_date="now")
        status = random.choices(statuses, weights=[15, 25, 25, 30, 5], k=1)[0]

        products_in_order = random.sample(products, k=random.randint(1, 5))
        total = 0.0

        for product in products_in_order:
            quantity = random.randint(1, 4)
            line_total = round(quantity * product["price"], 2)
            total += line_total
            order_items.append(
                {
                    "order_item_id": order_item_id,
                    "order_id": order_id,
                    "product_id": product["product_id"],
                    "quantity": quantity,
                    "unit_price": product["price"],
                    "line_total": line_total,
                }
            )
            order_item_id += 1

        orders.append(
            {
                "order_id": order_id,
                "user_id": user["user_id"],
                "order_date": order_date.strftime("%Y-%m-%d %H:%M:%S"),
                "status": status,
                "total_amount": round(total, 2),
            }
        )
    return orders, order_items


def generate_reviews(fake: Faker, users: list[dict], products: list[dict], max_reviews: int):
    reviews = []
    review_id = 1
    for _ in range(max_reviews):
        if random.random() < 0.55:  # 55% chance to create a review entry
            user = random.choice(users)
            product = random.choice(products)
            rating = random.randint(1, 5)
            reviews.append(
                {
                    "review_id": review_id,
                    "user_id": user["user_id"],
                    "product_id": product["product_id"],
                    "rating": rating,
                    "review_date": fake.date_between(start_date="-18m", end_date="today"),
                    "review_text": fake.sentence(nb_words=18),
                }
            )
            review_id += 1
    return reviews


def main(
    users_count: int = 500,
    products_count: int = 150,
    orders_count: int = 800,
    max_reviews: int = 400,
    seed: int | None = 42,
    output_dir: str = "data",
) -> None:
    if seed is not None:
        random.seed(seed)
        Faker.seed(seed)
    fake = Faker()

    users = generate_users(fake, users_count)
    products = generate_products(fake, products_count)
    orders, order_items = generate_orders(fake, users, products, orders_count)
    reviews = generate_reviews(fake, users, products, max_reviews)

    output_path = Path(output_dir)
    write_csv(output_path / "users.csv", users, list(users[0].keys()))
    write_csv(output_path / "products.csv", products, list(products[0].keys()))
    write_csv(output_path / "orders.csv", orders, list(orders[0].keys()))
    write_csv(output_path / "order_items.csv", order_items, list(order_items[0].keys()))
    if reviews:
        write_csv(output_path / "reviews.csv", reviews, list(reviews[0].keys()))

    print(f"Generated data in {output_path.resolve()}")


if __name__ == "__main__":
    main()

