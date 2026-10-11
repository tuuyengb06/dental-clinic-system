# Prompt: Sinh SQL báo cáo doanh thu bằng Zero-Shot

## Kỹ thuật minh họa

Zero-Shot Prompting cho tác vụ lập trình phổ biến, có ràng buộc rõ.

## Prompt sử dụng

Viết truy vấn SQL cho SQLite để thống kê doanh thu theo ngày trong một khoảng thời gian cho hệ thống quản lý nha khoa.

Giả định bảng dữ liệu:

- invoices(id, patient_id, invoice_date, status, payment_method, discount_amount, total_amount)
- invoice_items(id, invoice_id, dental_service_id, quantity, unit_price)
- dental_services(id, service_name)

Ràng buộc:

- Chỉ tính hóa đơn có `status = 'paid'`.
- Khoảng thời gian được truyền bằng hai tham số: `:from_date` và `:to_date`, bao gồm cả hai ngày.
- `invoice_date` được lưu theo định dạng ISO 8601.
- Kết quả gồm: `sale_date`, `invoice_count`, `gross_revenue`, `discount_total`, `net_revenue`.
- `gross_revenue` là tổng `quantity * unit_price` của các dòng dịch vụ nha khoa trên hóa đơn đã thanh toán.
- `discount_total` là tổng `discount_amount` của các hóa đơn trong ngày; nếu giá trị có thể là `NULL`, xem như 0.
- `net_revenue` là tổng `total_amount` của các hóa đơn đã thanh toán. Giả định `total_amount` đã là số tiền sau giảm giá.
- Mỗi hóa đơn có thể có nhiều dòng dịch vụ; không được nhân lặp tổng hóa đơn khi nối bảng.
- Chỉ trả về dữ liệu tổng hợp theo ngày; không truy vấn hoặc hiển thị thông tin định danh bệnh nhân.
- Sắp xếp theo `sale_date` tăng dần.

Đầu ra:

- Chỉ trả về câu SQL.
- Không giải thích thêm.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `01-Vi-du-prompt.md` thì file kết quả phải là `01-Vi-du-prompt_ket_qua.md`.
