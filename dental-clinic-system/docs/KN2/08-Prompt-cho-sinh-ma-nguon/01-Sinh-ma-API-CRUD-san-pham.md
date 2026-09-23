# Prompt: Sinh API CRUD Quản lý Vật tư Y tế & Dịch vụ Nha khoa

## Kỹ thuật minh họa
Prompt cho sinh mã nguồn: Instructions + Tech Stack + Constraints + Output Format.

## Prompt sử dụng

[Instructions]
Tạo API CRUD quản lý danh mục Vật tư Y tế (thuốc, mắc cài, implant, vật liệu trám...) và Dịch vụ Điều trị cho Hệ thống Quản lý Phòng khám Nha khoa Tích hợp AI.

[Context]
- Bạn là Lập trình viên Backend Python Senior chuyên về hệ thống y tế.
- Dự án demo sử dụng FastAPI, SQLAlchemy (ORM), Pydantic v2 và CSDL SQLite/PostgreSQL.
- Frontend (React/Vue) và phân hệ AI (Agent/RAG) sẽ gọi API này để truy vấn danh mục vật tư, cập nhật định mức tồn kho và lập hóa đơn điều trị.

[Constraints]
- Entity `MedicalSupply` (Vật tư y tế) gồm: `id`, `code` (Mã vật tư), `name` (Tên vật tư), `category_id` (Nhóm vật tư), `unit` (Đơn vị tính: hộp, cái, ống...), `cost_price` (Giá nhập), `selling_price` (Giá xuất/bán), `stock_quantity` (Số lượng tồn kho), `min_threshold` (Hạn mức tồn tối thiểu), `status` (Trạng thái: `active`, `inactive`).
- `code` và `name` là các trường bắt buộc (`nullable=False`), `code` phải là duy nhất (`unique=True`).
- `cost_price`, `selling_price`, `stock_quantity` và `min_threshold` không được mang giá trị âm ($\ge 0$).
- `status` chỉ nhận một trong hai giá trị: `active`, `inactive`.
- Các Endpoint API cần thiết:
  1. `POST /supplies/`: Tạo mới vật tư y tế.
  2. `GET /supplies/`: Xem danh sách (có hỗ trợ phân trang `skip`, `limit` và lọc theo `category_id`, `status`).
  3. `GET /supplies/{supply_id}`: Xem chi tiết 1 vật tư.
  4. `PUT /supplies/{supply_id}`: Cập nhật thông tin vật tư.
  5. `PATCH /supplies/{supply_id}/deactivate`: Ngừng sử dụng vật tư (chuyển `status = 'inactive'`).
- Không hardcode API key, chuỗi kết nối CSDL hoặc cấu hình nhạy cảm.
- Trả về chuẩn JSON response kèm HTTP status code phù hợp (`201 Created`, `200 OK`, `404 Not Found`, `400 Bad Request`).

[Output Format]
Trả về mã nguồn Python hoàn chỉnh gồm:
1. **SQLAlchemy Model** (`MedicalSupply`).
2. **Pydantic Schemas** (`Base`, `Create`, `Update`, `Response`).
3. **FastAPI Router** với đầy đủ các Endpoint yêu cầu.
4. Ghi chú ngắn gọn cách nhúng (`include_router`) vào ứng dụng FastAPI chính (`main.py`).

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `17-Sinh-api-crud-nha-khoa.md` thì file kết quả phải là `17-Sinh-api-crud-nha-khoa_ket_qua.md`.