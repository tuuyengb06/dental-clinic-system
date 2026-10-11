# Hỏi đáp dữ liệu hoạt động phòng khám bằng ReAct

## Bảng ReAct

| Bước | Kế hoạch/Hành động | Quan sát |
|---|---|---|
| 1 — Xác định dữ liệu | Cần giao dịch paid trong tháng hiện tại, số lượng theo dịch vụ, ánh xạ dịch vụ-vật tư, định mức `quantity_per_service`, và tồn vật tư hiện tại. Cần xác nhận timezone, ngưỡng “ít”/“cao”, trạng thái vật tư, và liệu vật tư liên quan nhiều dịch vụ có định mức cập nhật không. | Câu hỏi không cung cấp ngưỡng so sánh hay dữ liệu kết quả thực tế. Không thể gắn nhãn “ít/cao” một cách khách quan. |
| 2 — Hạn chế truy vấn | Dùng truy vấn SELECT-only dưới đây. Không truy cập patient, hồ sơ sức khỏe hay thông tin thanh toán cá nhân. | Đây là SQL đề xuất, không phải truy vấn đã thực thi. |
| 3 — Kiểm tra kết quả | Kiểm tra returned rows, số liệu tháng, mapping/denominator thiếu, và trường hợp không có usage. | Chưa có kết nối CSDL hoặc kết quả truy vấn; không có số liệu quan sát. |
| 4 — Trả lời | Yêu cầu người dùng/người cấu hình xác định ngưỡng hoặc chỉ hiển thị thứ hạng/số liệu thô cho họ tự lọc. | Câu trả lời bên dưới chỉ là mẫu, không phải dữ liệu thực tế. |

## SQL đề xuất (SQLite, chỉ đọc)

```sql
WITH monthly_usage AS (
    SELECT
        ii.dental_service_id,
        SUM(ii.quantity) AS paid_quantity
    FROM invoices AS i
    JOIN invoice_items AS ii ON ii.invoice_id = i.id
    WHERE i.status = 'paid'
      AND date(i.invoice_date) >= date('now', 'start of month')
      AND date(i.invoice_date) < date('now', 'start of month', '+1 month')
    GROUP BY ii.dental_service_id
),
service_set AS (
    SELECT id, service_code, name, status
    FROM dental_services
),
service_materials AS (
    SELECT
        s.dental_service_id,
        s.inventory_item_id,
        s.quantity_per_service
    FROM service_inventory_items AS s
)
SELECT
    ds.id AS dental_service_id,
    ds.service_code,
    ds.name AS service_name,
    ds.status AS service_status,
    COALESCE(mu.paid_quantity, 0) AS paid_quantity_this_month,
    sim.inventory_item_id,
    ii.item_code,
    ii.name AS inventory_item_name,
    ii.stock_quantity,
    ii.status AS inventory_status,
    sim.quantity_per_service,
    CASE
        WHEN sim.inventory_item_id IS NULL THEN 'missing_mapping'
        WHEN sim.quantity_per_service IS NULL THEN 'missing_usage_rate'
        ELSE 'mapped'
    END AS mapping_status
FROM service_set AS ds
LEFT JOIN monthly_usage AS mu
    ON mu.dental_service_id = ds.id
LEFT JOIN service_materials AS sim
    ON sim.dental_service_id = ds.id
LEFT JOIN inventory_items AS ii
    ON ii.id = sim.inventory_item_id
ORDER BY paid_quantity_this_month ASC, ds.id ASC, sim.inventory_item_id ASC;
```

### Cách kiểm tra kết quả

- Không có service rows: danh mục rỗng hoặc query/date schema cần kiểm tra.
- Dịch vụ có `paid_quantity_this_month = 0`: không có dòng dịch vụ trên hóa đơn paid trong kỳ; không suy ra dịch vụ “ít” nếu chưa có baseline/ngưỡng.
- `mapping_status` khác `mapped`, hoặc tồn/định mức NULL: không thể kết luận tồn vật tư liên quan.
- Dịch vụ liên kết nhiều vật tư trả nhiều dòng; không cộng tồn các dòng nếu một vật tư được ánh xạ lặp, cần kiểm tra dữ liệu mapping.
- Truy vấn gồm cả dịch vụ/vật tư inactive do câu hỏi chưa yêu cầu lọc; cần chốt chính sách.
- `date('now')` dùng ngày UTC của SQLite. Nếu báo cáo theo timezone phòng khám, truyền ranh giới ngày đã chuẩn hóa làm parameters thay vì giả định UTC.

## Câu trả lời mẫu cho chủ phòng khám

> Tôi có thể đối chiếu số lượt dịch vụ đã thanh toán trong tháng với lượng tồn của các vật tư được ánh xạ, nhưng hiện chưa có dữ liệu truy vấn và chưa có ngưỡng định nghĩa “ít” hoặc “tồn kho cao”. Vì vậy tôi chưa thể nêu dịch vụ nào đáp ứng tiêu chí. Vui lòng xác nhận ngưỡng (hoặc yêu cầu sắp xếp theo số lượng/tồn thô) và timezone báo cáo; sau đó cần kiểm tra mapping/định mức trước khi kết luận.

**Trạng thái quan sát:** chưa thực sự truy vấn CSDL. SQL và câu trả lời trên chỉ là đề xuất/mẫu; không có số liệu thực tế.
