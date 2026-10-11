# Kiểm chứng SQL: Dịch vụ được thực hiện nhiều nhất

Ba cách tiếp cận dưới đây giả định `invoice_date` là chuỗi ISO-8601 mà hàm `date()` SQLite phân tích được. Khoảng ngày được hiểu theo ngày lịch, bao gồm cả hai ngày; các truy vấn chỉ dùng hóa đơn `paid` và không truy cập bảng bệnh nhân.

## Phương án 1 — JOIN và GROUP BY trực tiếp

```sql
SELECT
    ds.id AS dental_service_id,
    ds.service_code,
    ds.name,
    SUM(ii.quantity) AS total_quantity,
    SUM(ii.quantity * ii.unit_price) AS total_revenue
FROM invoices AS i
JOIN invoice_items AS ii ON ii.invoice_id = i.id
JOIN dental_services AS ds ON ds.id = ii.dental_service_id
WHERE i.status = 'paid'
  AND date(i.invoice_date) BETWEEN date(:from_date) AND date(:to_date)
GROUP BY ds.id, ds.service_code, ds.name
ORDER BY total_quantity DESC, total_revenue DESC, ds.id ASC
LIMIT 10;
```

## Phương án 2 — Lọc hóa đơn trước, sau đó tổng hợp dòng

```sql
WITH paid_invoices AS (
    SELECT id
    FROM invoices
    WHERE status = 'paid'
      AND date(invoice_date) BETWEEN date(:from_date) AND date(:to_date)
)
SELECT
    ds.id AS dental_service_id,
    ds.service_code,
    ds.name,
    SUM(ii.quantity) AS total_quantity,
    SUM(ii.quantity * ii.unit_price) AS total_revenue
FROM paid_invoices AS pi
JOIN invoice_items AS ii ON ii.invoice_id = pi.id
JOIN dental_services AS ds ON ds.id = ii.dental_service_id
GROUP BY ds.id, ds.service_code, ds.name
ORDER BY total_quantity DESC, total_revenue DESC, ds.id ASC
LIMIT 10;
```

## Phương án 3 — Tổng hợp dòng hóa đơn trước khi nối danh mục

```sql
WITH paid_invoices AS (
    SELECT id
    FROM invoices
    WHERE status = 'paid'
      AND date(invoice_date) BETWEEN date(:from_date) AND date(:to_date)
),
service_totals AS (
    SELECT
        ii.dental_service_id,
        SUM(ii.quantity) AS total_quantity,
        SUM(ii.quantity * ii.unit_price) AS total_revenue
    FROM paid_invoices AS pi
    JOIN invoice_items AS ii ON ii.invoice_id = pi.id
    GROUP BY ii.dental_service_id
)
SELECT
    ds.id AS dental_service_id,
    ds.service_code,
    ds.name,
    st.total_quantity,
    st.total_revenue
FROM service_totals AS st
JOIN dental_services AS ds ON ds.id = st.dental_service_id
ORDER BY st.total_quantity DESC, st.total_revenue DESC, ds.id ASC
LIMIT 10;
```

## Bảng kiểm tra edge case

| Edge case | Kết quả mong đợi |
|---|---|
| Không có hóa đơn paid trong kỳ | Không có dòng kết quả; không phát sinh lỗi |
| Hóa đơn cancelled/unpaid | Không được tính vì điều kiện `status='paid'` |
| Dịch vụ inactive có giao dịch paid trong kỳ | Vẫn có thể xuất hiện: truy vấn không lọc trạng thái dịch vụ để giữ báo cáo lịch sử; nếu nghiệp vụ muốn loại thì phải xác định rõ |
| Nhiều dòng cùng dịch vụ | SUM(quantity) và SUM(quantity * unit_price) gộp đúng |
| Bằng total_quantity và total_revenue | `dental_service_id` tăng dần tạo thứ tự ổn định |

## Truy vấn cuối cùng

Chọn **Phương án 3** vì lọc hóa đơn hợp lệ trước, tổng hợp theo dịch vụ rồi mới lấy thông tin danh mục; tổng không bị nhân lên bởi các quan hệ khác và tie-break được xác định rõ.

```sql
WITH paid_invoices AS (
    SELECT id
    FROM invoices
    WHERE status = 'paid'
      AND date(invoice_date) BETWEEN date(:from_date) AND date(:to_date)
),
service_totals AS (
    SELECT
        ii.dental_service_id,
        SUM(ii.quantity) AS total_quantity,
        SUM(ii.quantity * ii.unit_price) AS total_revenue
    FROM paid_invoices AS pi
    JOIN invoice_items AS ii ON ii.invoice_id = pi.id
    GROUP BY ii.dental_service_id
)
SELECT
    ds.id AS dental_service_id,
    ds.service_code,
    ds.name,
    st.total_quantity,
    st.total_revenue
FROM service_totals AS st
JOIN dental_services AS ds ON ds.id = st.dental_service_id
ORDER BY st.total_quantity DESC, st.total_revenue DESC, ds.id ASC
LIMIT 10;
```

**Giả định:** ID dịch vụ tồn tại trong danh mục; invoice item có số lượng/đơn giá hợp lệ. Nếu ngày lưu có timezone/offset mà báo cáo phải theo timezone phòng khám, cần chuẩn hóa ranh giới thời gian trước khi dùng `date()`.
