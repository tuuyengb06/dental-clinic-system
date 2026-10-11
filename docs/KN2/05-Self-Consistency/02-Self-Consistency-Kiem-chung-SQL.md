# Prompt: Kiểm chứng SQL bằng Self-Consistency

## Kỹ thuật minh họa

Self-Consistency cho tác vụ có đáp án khách quan và có thể kiểm tra.

## Prompt sử dụng

Bạn là chuyên gia SQL. Hãy tạo 3 cách tiếp cận độc lập để viết truy vấn tìm các dịch vụ nha khoa được thực hiện nhiều nhất trong hệ thống quản lý phòng khám, sau đó chọn truy vấn đáng tin cậy nhất.

Lược đồ:

- dental_services(id, service_code, name, category_id, price, status)
- invoices(id, invoice_date, status, total_amount)
- invoice_items(id, invoice_id, dental_service_id, quantity, unit_price)

Yêu cầu:

- Tìm 10 dịch vụ có tổng số lượng cao nhất trong khoảng `:from_date` đến `:to_date`, bao gồm cả hai ngày.
- Chỉ tính hóa đơn có `status = 'paid'`.
- Một dịch vụ được xem là thực hiện nhiều nhất dựa trên tổng `quantity` trong các dòng hóa đơn hợp lệ.
- Kết quả gồm `dental_service_id`, `service_code`, `name`, `total_quantity`, `total_revenue`.
- `total_revenue` được tính bằng tổng `quantity * unit_price`.
- Sắp xếp theo `total_quantity` giảm dần; nếu bằng nhau thì `total_revenue` giảm dần; nếu vẫn bằng nhau thì `dental_service_id` tăng dần để kết quả ổn định.
- Chỉ sử dụng dữ liệu tổng hợp, không truy vấn hoặc hiển thị thông tin định danh bệnh nhân.
- Nếu trạng thái `status` của dịch vụ không được dùng làm điều kiện lọc, hãy giải thích vì sao dịch vụ ngừng hoạt động vẫn có thể xuất hiện trong báo cáo lịch sử. Không tự loại dịch vụ ngừng hoạt động nếu yêu cầu chưa quy định.

Quy trình:

1. Viết 3 truy vấn có cách tiếp cận khác nhau nếu hợp lý.
2. Tự kiểm tra từng truy vấn với edge case: không có hóa đơn đã thanh toán trong khoảng thời gian, hóa đơn bị hủy hoặc chưa thanh toán, dịch vụ đã ngừng hoạt động nhưng có giao dịch lịch sử, nhiều dòng hóa đơn cho cùng một dịch vụ và trường hợp bằng điểm.
3. Chọn truy vấn cuối cùng và giải thích ngắn gọn tính đúng đắn cùng các giả định.

Định dạng đầu ra:

1. Phương án 1
2. Phương án 2
3. Phương án 3
4. Bảng kiểm tra edge case
5. Truy vấn cuối cùng

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `01-Vi-du-prompt.md` thì file kết quả phải là `01-Vi-du-prompt_ket_qua.md`.
