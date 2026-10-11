# Prompt: Sinh API CRUD quản lý dịch vụ nha khoa

## Kỹ thuật minh họa

Prompt cho sinh mã nguồn: Instructions + tech stack + constraints + output format.

## Prompt sử dụng

[Instructions]

Tạo API CRUD quản lý dịch vụ nha khoa cho hệ thống quản lý phòng khám nha khoa có tích hợp AI.

[Context]

- Bạn là lập trình viên backend Python senior.
- Dự án demo dùng FastAPI, SQLAlchemy và SQLite.
- Frontend sẽ gọi API để quản lý danh mục dịch vụ nha khoa.
- Danh mục dịch vụ cung cấp dữ liệu chuẩn cho các chức năng đặt lịch, lập hóa đơn và chatbot cung cấp thông tin dịch vụ.

[Constraints]

- Entity `DentalService` gồm: `id`, `service_code`, `name`, `category`, `description`, `price`, `duration_minutes`, `status`.
- `service_code` và `name` là bắt buộc; `service_code` phải duy nhất.
- `price` không được âm.
- `duration_minutes` phải là số nguyên dương.
- `status` chỉ nhận: `active`, `inactive`.
- API cần có các endpoint: tạo dịch vụ, xem danh sách, xem chi tiết, cập nhật và ngừng cung cấp dịch vụ.
- Dịch vụ đã được sử dụng trong hóa đơn hoặc hồ sơ khác không được xóa vật lý; dùng trạng thái `inactive` để ngừng cung cấp.
- Không đưa vào endpoint này thông tin bệnh nhân, hồ sơ sức khỏe hoặc dữ liệu thanh toán.
- Không hardcode API key hoặc cấu hình nhạy cảm.
- Trả về JSON với HTTP status code phù hợp; xử lý rõ các trường hợp dữ liệu không hợp lệ, không tìm thấy dịch vụ hoặc trùng `service_code`.
- Dùng kiểu dữ liệu phù hợp cho tiền tệ và nêu rõ cách biểu diễn/serialize giá trong JSON.

[Output Format]

Trả về code gồm:

1. SQLAlchemy model.
2. Pydantic schemas.
3. FastAPI router với các endpoint CRUD cần thiết.
4. Ghi chú ngắn cách include router vào app chính.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `01-Vi-du-prompt.md` thì file kết quả phải là `01-Vi-du-prompt_ket_qua.md`.
