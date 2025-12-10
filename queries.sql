-- Top 10 users by total spending (orders total_amount)
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

-- Top 10 products by revenue (sum of order_items line_total)
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

-- Average rating per product (only products with reviews)
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

-- Country-level revenue (sum of order totals by user country)
SELECT
    u.country,
    SUM(o.total_amount) AS revenue,
    COUNT(DISTINCT o.order_id) AS orders_count,
    COUNT(DISTINCT u.user_id) AS users_count
FROM users u
JOIN orders o ON o.user_id = u.user_id
GROUP BY u.country
ORDER BY revenue DESC;

