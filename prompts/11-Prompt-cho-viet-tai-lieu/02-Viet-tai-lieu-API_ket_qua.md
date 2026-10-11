# Tài liệu API (bản dự kiến)

> Các endpoint dưới đây là dự kiến theo đầu vào, không phải bằng chứng API đã triển khai. Quyền và quy tắc chưa được nêu được đánh dấu cần xác nhận.

## 1. Quy ước chung

- Giao thức: HTTP; nội dung JSON UTF-8.
- Base URL/version: cần xác nhận.
- Xác thực: cần xác nhận cơ chế token/session; mọi endpoint cần kiểm tra quyền ở backend.
- ID minh họa là giả; không đưa thông tin định danh hoặc sức khỏe bệnh nhân vào ví dụ.
- Lỗi dự kiến: `400` input sai, `401` chưa xác thực, `403` không đủ quyền, `404` không tìm thấy, `409` xung đột nghiệp vụ, `422` validation, `500` lỗi không dự kiến. Mã thực tế cần thống nhất.

## 2. Bảng endpoint

| Method | Endpoint | Mục đích | Quyền dự kiến/cần xác nhận |
|---|---|---|---|
| POST | `/dental-services` | Tạo dịch vụ | Nhân viên được cấp quyền quản lý danh mục |
| GET | `/dental-services` | Danh sách, tìm kiếm/lọc trạng thái | Phạm vi đọc cần xác nhận |
| PATCH | `/dental-services/{id}` | Cập nhật dịch vụ | Nhân viên được cấp quyền |
| POST | `/appointments` | Tạo lịch hẹn | Lễ tân/nhân viên được cấp quyền |
| POST | `/invoices` | Tạo hóa đơn | Nhân viên được cấp quyền |
| PATCH | `/invoices/{id}/cancel` | Hủy hóa đơn theo luồng được cho phép | Vai trò và điều kiện hủy cần xác nhận |
| GET | `/reports/revenue` | Báo cáo doanh thu kỳ chọn | Chủ phòng khám/role được cấp quyền; không trả thông tin bệnh nhân |

## 3. Chi tiết endpoint

### `POST /dental-services`

- **Mục đích:** tạo dịch vụ nha khoa.
- **Quyền:** cần xác nhận role quản lý danh mục.
- **Request body (minh họa):**

```json
{
  "service_code": "SRV-DEMO-01",
  "name": "Trám răng Composite",
  "description": "Mô tả dịch vụ giả lập",
  "price": 350000,
  "duration_minutes": 45,
  "status": "active"
}
```

- **201 response:** `{"id": 101, "service_code": "SRV-DEMO-01", "name": "Trám răng Composite", "price": 350000, "status": "active"}`
- **Lỗi:** 422 validation; 409 mã dịch vụ trùng; 401/403 theo xác thực/quyền.

### `GET /dental-services`

- **Query params:** `search` tùy chọn; `status=active|inactive` tùy chọn. Pagination/sort cần xác nhận.
- **Response 200:** danh sách DTO dịch vụ; không bao gồm dữ liệu bệnh nhân.
- **Lỗi:** 401/403; 422 nếu query không hợp lệ.

### `PATCH /dental-services/{id}`

- **Request body:** một phần trường dịch vụ đã xác nhận, ví dụ `{"price": 360000}`.
- **200 response:** dịch vụ sau cập nhật.
- **Lỗi:** 404 ID không có; 409 trùng service_code; 422 dữ liệu sai; 401/403.
- **Cần xác nhận:** dịch vụ đã tham chiếu hóa đơn có trường nào được sửa.

### `POST /appointments`

- **Request body minh họa:** `{"patient_ref":"PAT-DEMO-01","scheduled_at":"2026-10-20T09:00:00+07:00","service_id":101}`
- **Response 201:** ID và trạng thái lịch đã tạo; chỉ trả trường cần thiết cho caller.
- **Lỗi:** 404 tham chiếu không tồn tại; 409 nếu conflict theo quy tắc đã cấu hình; 422 input sai; 403 không đủ quyền.
- **Cần xác nhận:** bác sĩ/nhân viên phụ trách, trạng thái hợp lệ, quy tắc trùng lịch và múi giờ.

### `POST /invoices`

- **Request body minh họa:** `{"patient_ref":"PAT-DEMO-01","items":[{"service_id":101,"quantity":1}]}`
- **Response 201:** mã hóa đơn, tổng tiền, trạng thái; không trả hồ sơ sức khỏe.
- **Lỗi:** 404 tham chiếu thiếu; 409 xung đột; 422 dòng dịch vụ/số lượng sai; 403 quyền không đủ.
- **Cần xác nhận:** định nghĩa tổng/giảm giá, trạng thái thanh toán và thời điểm ghi nhận vật tư.

### `PATCH /invoices/{id}/cancel`

- **Request body:** chưa xác định; không giả định lý do/trạng thái nào được phép.
- **Response thành công:** mã hóa đơn và trạng thái sau xử lý.
- **Lỗi:** 404 không tìm thấy; 409 không thể hủy theo trạng thái/quy trình; 401/403.
- Hủy trạng thái thanh toán không đồng nghĩa điều trị bị đảo ngược hoặc vật tư được hoàn kho; việc hoàn/đảo phải theo quy tắc nghiệp vụ riêng.

### `GET /reports/revenue`

- **Query params:** `from_date`, `to_date` (inclusive hay exclusive cần xác nhận), tùy chọn bộ lọc được hỗ trợ.
- **Response 200 minh họa:** `{"from_date":"2026-10-01","to_date":"2026-10-31","currency":"VND","total_revenue":1350000}`
- **Lỗi:** 400/422 kỳ không hợp lệ; 401/403 quyền; 500 lỗi xử lý.
- Chỉ trả tổng hợp, không nối/trả patient identifiers, hồ sơ khám hoặc dữ liệu thanh toán cá nhân.

## 4. Lưu ý bảo mật và kiểm thử

- Thực thi authz tại backend; kiểm thử truy cập ngang vai trò và resource ownership.
- Validate input, chống truy vấn vượt quyền; không log token/body nhạy cảm.
- Test success, not-found, duplicate, invalid payload, quyền thiếu, hủy lặp, time boundary và không rò dữ liệu bệnh nhân.
- Không khẳng định schema, quyền hay hành vi nào đã thống nhất nếu chưa có đặc tả.
