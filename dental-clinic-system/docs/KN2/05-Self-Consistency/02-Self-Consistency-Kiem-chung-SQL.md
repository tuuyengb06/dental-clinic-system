# Prompt: Kiểm chứng SQL bằng Self-Consistency

## Kỹ thuật minh họa
Self-Consistency cho tác vụ có đáp án khách quan, yêu cầu độ chính xác cao và có thể kiểm chứng qua nhiều góc độ truy vấn.

## Prompt sử dụng

Bạn là chuyên gia cơ sở dữ liệu y tế. Hãy tạo 3 cách tiếp cận độc lập để viết truy vấn SQL tìm top dịch vụ nha khoa phát sinh nhiều nhất (hoặc mang lại doanh thu cao nhất) trong hệ thống quản lý phòng khám nha khoa tích hợp AI, sau đó phân tích và chọn truy vấn đáng tin cậy nhất.

Lược đồ cơ sở dữ liệu:
- `dental_services`(`id`, `code`, `name`, `category_id`, `standard_price`, `status`)
- `invoices`(`id`, `patient_id`, `doctor_id`, `invoice_date`, `status`, `discount_amount`, `total_amount`)
- `invoice_details`(`id`, `invoice_id`, `service_id`, `quantity`, `unit_price`, `subtotal`)

Yêu cầu nghiệp vụ:
- Tìm Top 10 dịch vụ nha khoa được thực hiện nhiều nhất trong khoảng thời gian từ `:from_date` đến `:to_date`.
- Chỉ tính các hóa đơn đã thanh toán hợp lệ (`status = 'completed'`).
- Kết quả trả về gồm: `service_id`, `code`, `name`, `total_quantity` (tổng số ca thực hiện), `total_revenue` (tổng doanh thu thực tế thu được từ dịch vụ đó).
- Sắp xếp kết quả theo `total_quantity` giảm dần, nếu bằng nhau thì sắp xếp theo `total_revenue` giảm dần.

Quy trình Self-Consistency:
1. Viết 3 câu truy vấn SQL với cách tiếp cận kỹ thuật khác nhau (ví dụ: `JOIN` truyền thống, `Subquery/CTE` lọc dữ liệu trước khi ghép, và dùng `WINDOW FUNCTION` hoặc `CTE` tối ưu hiệu năng).
2. Tự kiểm tra và đánh giá từng phương án với các trường hợp đặc biệt (Edge cases): khoảng thời gian không có lượt khám, hóa đơn bị hủy (`status = 'cancelled'`), dịch vụ đã ngừng cung cấp (`status = 'inactive'`), hóa đơn có chiết khấu/được giảm giá.
3. Chọn truy vấn tối ưu nhất về mặt hiệu năng, độ chính xác nghiệp vụ và tính minh bạch, sau đó giải thích ngắn gọn.

Định dạng đầu ra:
1. Phương án 1 (Implicit / Explicit JOIN đơn giản)
2. Phương án 2 (Sử dụng CTE / Subquery lọc trước khi JOIN)
3. Phương án 3 (Sử dụng Window Functions / Aggregation nâng cao)
4. Bảng kiểm tra và đánh giá Edge Cases
5. Truy vấn SQL cuối cùng được lựa chọn

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `12-Kiem-chung-sql-nha-khoa.md` thì file kết quả phải là `12-Kiem-chung-sql-nha-khoa_ket_qua.md`.