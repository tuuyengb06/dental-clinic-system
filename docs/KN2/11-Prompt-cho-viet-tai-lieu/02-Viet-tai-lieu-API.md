# Prompt: Viết tài liệu API

## Kỹ thuật minh họa

Prompt viết tài liệu kỹ thuật từ mô tả endpoint.

## Prompt sử dụng

[Instructions]

Viết tài liệu API cho các endpoint quản lý dịch vụ nha khoa, lịch hẹn, hóa đơn và báo cáo của hệ thống quản lý nha khoa tích hợp AI.

[Input]

Endpoint dự kiến:

- `POST /dental-services`: tạo dịch vụ nha khoa.
- `GET /dental-services`: xem danh sách dịch vụ, hỗ trợ tìm kiếm và lọc theo trạng thái.
- `PATCH /dental-services/{id}`: cập nhật thông tin dịch vụ.
- `POST /appointments`: tạo lịch hẹn.
- `POST /invoices`: tạo hóa đơn dịch vụ nha khoa.
- `PATCH /invoices/{id}/cancel`: hủy hóa đơn theo quy trình được hệ thống cho phép.
- `GET /reports/revenue`: thống kê doanh thu theo khoảng thời gian.

[Context]

- API trả về JSON.
- Cần có xác thực và phân quyền theo vai trò.
- Quyền truy cập hồ sơ bệnh nhân và dữ liệu lịch hẹn phải được giới hạn theo vai trò.
- Không đưa thông tin định danh bệnh nhân, hồ sơ sức khỏe hoặc dữ liệu thanh toán nhạy cảm vào ví dụ.
- Nếu thông tin về quy tắc nghiệp vụ, quyền truy cập, cấu trúc dữ liệu hoặc trạng thái chưa được cung cấp, hãy ghi rõ là cần xác nhận; không tự khẳng định như đặc tả đã thống nhất.
- Khi mô tả hủy hóa đơn, không giả định việc hủy luôn hoàn lại vật tư; cần phân biệt trạng thái thanh toán với việc điều trị/vật tư đã thực hiện hoặc tiêu hao.

[Output Format]

Markdown gồm:

1. Quy ước chung.
2. Bảng danh sách endpoint.
3. Chi tiết từng endpoint: mục đích, quyền truy cập, request body/query params, response thành công và lỗi thường gặp.
4. Ví dụ JSON cho request/response, chỉ sử dụng dữ liệu giả lập không định danh.
5. Lưu ý bảo mật và kiểm thử.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `01-Vi-du-prompt.md` thì file kết quả phải là `01-Vi-du-prompt_ket_qua.md`.
