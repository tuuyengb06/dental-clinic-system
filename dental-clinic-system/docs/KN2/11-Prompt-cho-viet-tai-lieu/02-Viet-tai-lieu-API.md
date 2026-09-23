# Prompt: Viết tài liệu API cho Hệ thống Quản lý Nha khoa Tích hợp AI

## Kỹ thuật minh họa
Prompt viết tài liệu kỹ thuật từ mô tả các RESTful Endpoints, tích hợp các ràng buộc an toàn thông tin y tế và xử lý các dịch vụ AI chuyên sâu.

## Prompt sử dụng

[Instructions]
Viết tài liệu API RESTful chi tiết cho các endpoint quản lý hồ sơ bệnh nhân, lịch hẹn điều trị nha khoa, vật tư y tế và tích hợp dịch vụ AI trong Hệ thống Quản lý Phòng khám Nha khoa Tích hợp AI.

[Input]
Danh sách endpoints dự kiến:
- `POST /api/v1/patients`: Tạo mới hồ sơ bệnh nhân (bao gồm thông tin tiền sử bệnh lý nha khoa).
- `GET /api/v1/patients`: Tra cứu danh sách bệnh nhân (hỗ trợ tìm kiếm theo Họ tên/Số điện thoại và lọc theo Bác sĩ phụ trách).
- `PATCH /api/v1/patients/{id}`: Cập nhật thông tin hồ sơ bệnh nhân hoặc cập nhật sơ đồ răng (Dental Chart).
- `POST /api/v1/appointments`: Đặt lịch khám / đặt lịch điều trị nha khoa.
- `PATCH /api/v1/appointments/{id}/cancel`: Hủy lịch hẹn và giải phóng ca làm việc của Bác sĩ.
- `POST /api/v1/ai/analyze-xray`: Gửi ảnh X-quang răng để AI phân tích phát hiện sâu răng/răng khôn lệch và đề xuất chẩn đoán.
- `GET /api/v1/reports/revenue`: Thống kê doanh thu phòng khám và phân tích hiệu suất dịch vụ theo khoảng thời gian.

[Context]
- Tất cả API trả về định dạng JSON tiêu chuẩn.
- Hệ thống bắt buộc xác thực qua Bearer Token (JWT) và phân quyền chặt chẽ dựa trên vai trò (Role-Based Access Control - RBAC: `Admin`, `Dentist`, `Receptionist`, `Patient`).
- Nghiêm cấm đưa các thông tin nhạy cảm của bệnh nhân (như Số định danh cá nhân, dữ liệu thẻ thanh toán ngân hàng, hình ảnh riêng tư chưa anonymize) vào ví dụ mẫu (Tuân thủ chuẩn bảo mật PII/PHI).

[Output Format]
Định dạng bài viết bằng Markdown gồm 5 mục tiêu chuẩn:
1. **Quy ước chung:** Định dạng dữ liệu (JSON), Mã trạng thái HTTP (200, 201, 400, 401, 403, 404, 500), Chuẩn Authentication (JWT Header) và Phân quyền RBAC.
2. **Bảng danh sách Endpoint:** Bảng tổng quan gồm các cột (Method, Endpoint, Mục tính năng, Quyền tối thiểu).
3. **Chi tiết từng Endpoint:** Với mỗi endpoint trình bày: Mục đích, Quyền truy cập, Path/Query parameters, Request Body schema, Successful Response schema, Error Codes thường gặp.
4. **Ví dụ JSON mẫu:** Mẫu Request/Response JSON hoàn chỉnh, thực tế cho từng endpoint.
5. **Lưu ý bảo mật & Kiểm thử:** Hướng dẫn bảo vệ dữ liệu y tế (encryption/masking), Rate Limiting khi gọi API AI, và cách mock API để viết Integration Test.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `25-Viet-tai-lieu-api-nha-khoa.md` thì file kết quả phải là `25-Viet-tai-lieu-api-nha-khoa_ket_qua.md`.