# Prompt: Sinh SQL báo cáo doanh thu bằng Zero-Shot

## Kỹ thuật minh họa
Zero-Shot Prompting cho tác vụ lập trình phổ biến, có ràng buộc rõ.

## Prompt sử dụng

Viết truy vấn SQL cho SQLite để thống kê doanh thu điều trị nha khoa theo ngày trong một khoảng thời gian cho hệ thống quản lý phòng khám nha khoa.

Giả định bảng dữ liệu:
- invoices(id, patient_id, doctor_id, invoice_date, status, payment_method, discount_amount, total_amount)
- invoice_details(id, invoice_id, service_id, quantity, unit_price)

Ràng buộc:
- Chỉ tính hóa đơn đã thanh toán hoàn tất với status = 'completed'.
- Khoảng thời gian được lọc bằng hai tham số: :from_date và :to_date.
- Kết quả trả về gồm: sale_date, invoice_count, gross_revenue, total_discount, net_revenue.
- gross_revenue là tổng chi phí dịch vụ ban đầu (tổng quantity * unit_price từ invoice_details).
- net_revenue là doanh thu thực tế thu được (tổng total_amount sau khi đã trừ discount_amount).
- Sắp xếp kết quả theo sale_date tăng dần.

Đầu ra:
- Chỉ trả về câu SQL.
- Không giải thích thêm.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `04-Sinh-sql-doanh-thu-nha-khoa.md` thì file kết quả phải là `04-Sinh-sql-doanh-thu-nha-khoa_ket_qua.md`.