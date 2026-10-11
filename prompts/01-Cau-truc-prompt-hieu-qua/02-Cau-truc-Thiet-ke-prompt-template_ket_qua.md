# Prompt template tái sử dụng cho dự án nha khoa tích hợp AI

## 1. Prompt template

```text
{{vai_tro}}

Bối cảnh dự án:
{{boi_canh_du_an}}

Nhiệm vụ:
{{nhiem_vu}}

Đầu vào:
{{dau_vao}}

Ràng buộc:
- Chỉ dựa trên thông tin đầu vào; không tự bịa dữ kiện hoặc quy tắc nghiệp vụ.
- Nếu thiếu thông tin quan trọng, hãy nêu giả định/điểm cần xác nhận hoặc hỏi lại.
- Không đưa dữ liệu định danh, hồ sơ sức khỏe, dữ liệu thanh toán cá nhân,
  mật khẩu hay API key của người thật; dùng dữ liệu giả lập/đã khử định danh.
- Nếu nội dung liên quan chuyên môn nha khoa, không chẩn đoán hoặc quyết định
  điều trị thay bác sĩ; ghi rõ nội dung AI chỉ hỗ trợ và cần người có thẩm quyền
  xem xét trước khi sử dụng.
{{rang_buoc}}

Tiêu chí đạt:
{{tieu_chi_dat}}

Định dạng đầu ra:
{{dinh_dang_dau_ra}}
```

## 2. Giải thích placeholder

| Placeholder | Cách điền |
|---|---|
| `{{vai_tro}}` | Nêu vai trò/chuyên môn AI cần mô phỏng, ví dụ “Bạn là lập trình viên backend Python”. |
| `{{boi_canh_du_an}}` | Chỉ điền thông tin dự án liên quan tác vụ: nghiệp vụ, stack đã xác nhận, người dùng và giới hạn. |
| `{{nhiem_vu}}` | Mô tả động từ và kết quả cụ thể cần tạo, tránh gộp nhiều mục tiêu không liên quan. |
| `{{dau_vao}}` | Đưa lược đồ, đoạn code, yêu cầu hoặc dữ liệu giả lập cần xử lý; loại bỏ dữ liệu thật nhạy cảm. |
| `{{rang_buoc}}` | Bổ sung quy tắc kỹ thuật/nghiệp vụ cụ thể như phiên bản thư viện, quyền, phạm vi, điều không được làm. |
| `{{tieu_chi_dat}}` | Đưa tiêu chí kiểm chứng được: nội dung bắt buộc, edge case, test hoặc giới hạn. |
| `{{dinh_dang_dau_ra}}` | Chỉ rõ cấu trúc Markdown/bảng/code, tên mục, ngôn ngữ và có/không giải thích. |

## 3. Ví dụ đã điền: sinh API CRUD dịch vụ nha khoa

```text
Bạn là lập trình viên backend Python.

Bối cảnh dự án:
Bản demo quản lý danh mục dịch vụ nha khoa; stack đã chọn FastAPI,
SQLAlchemy và SQLite. API được frontend gọi. Danh mục dịch vụ có thể
được dùng khi đặt lịch, lập hóa đơn và hiển thị thông tin dịch vụ.

Nhiệm vụ:
Tạo model, schema và router CRUD cho DentalService.

Đầu vào:
DentalService gồm id, service_code, name, category, description, price,
duration_minutes, status. service_code duy nhất; name và service_code bắt buộc.

Ràng buộc:
- price không âm; duration_minutes là số nguyên dương.
- status chỉ nhận active hoặc inactive.
- Có endpoint tạo, liệt kê, xem chi tiết, cập nhật và ngừng cung cấp.
- Không xóa vật lý dịch vụ đã được dùng; ngừng cung cấp bằng status=inactive.
- Không đưa thông tin bệnh nhân, hồ sơ sức khỏe hoặc dữ liệu thanh toán vào API.
- Không hardcode API key hoặc bí mật.
- Nếu thiếu phiên bản thư viện hay cấu trúc dự án, nêu giả định; không khẳng định
  tương thích với cấu hình chưa được cung cấp.

Tiêu chí đạt:
- Trả lỗi phù hợp khi dữ liệu không hợp lệ, không tìm thấy id hoặc trùng
  service_code.
- Giá có kiểu biểu diễn tiền tệ nhất quán; giải thích cách serialize.

Định dạng đầu ra:
1. SQLAlchemy model.
2. Pydantic schemas.
3. FastAPI router đầy đủ các endpoint cần thiết.
4. Ghi chú ngắn cách include router vào app chính.
```
