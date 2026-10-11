WITH invoice_item_totals AS (
    SELECT
        invoice_id,
        SUM(quantity * unit_price) AS gross_revenue
    FROM invoice_items
    GROUP BY invoice_id
),
paid_invoices AS (
    SELECT
        i.id,
        date(i.invoice_date) AS sale_date,
        COALESCE(i.discount_amount, 0) AS discount_amount,
        i.total_amount
    FROM invoices AS i
    WHERE i.status = 'paid'
      AND date(i.invoice_date) BETWEEN date(:from_date) AND date(:to_date)
)
SELECT
    p.sale_date AS sale_date,
    COUNT(*) AS invoice_count,
    COALESCE(SUM(it.gross_revenue), 0) AS gross_revenue,
    SUM(p.discount_amount) AS discount_total,
    SUM(p.total_amount) AS net_revenue
FROM paid_invoices AS p
LEFT JOIN invoice_item_totals AS it
    ON it.invoice_id = p.id
GROUP BY p.sale_date
ORDER BY p.sale_date ASC;
