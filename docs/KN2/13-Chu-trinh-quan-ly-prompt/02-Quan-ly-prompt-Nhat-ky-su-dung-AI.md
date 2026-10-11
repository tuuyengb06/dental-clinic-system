# Prompt: Tạo nhật ký sử dụng AI

## Kỹ thuật minh họa

Prompt Management Cycle trong thực hành: ghi nhận prompt, phản hồi, đánh giá và tinh chỉnh.

## Prompt sử dụng

[Instructions]

Tạo mẫu nhật ký sử dụng AI cho sinh viên phát triển hệ thống quản lý nha khoa tích hợp AI.

[Context]

- Nhật ký dùng để minh chứng việc sử dụng AI trong các giai đoạn SDLC: phân tích, thiết kế, lập trình, kiểm thử và viết tài liệu.
- Cần ghi rõ prompt đã dùng, phản hồi AI, phần sinh viên kiểm chứng hoặc chỉnh sửa và kết quả cuối cùng.
- Không lưu dữ liệu nhạy cảm như thông tin định danh bệnh nhân, hồ sơ sức khỏe, thông tin thanh toán cá nhân, mật khẩu hoặc API key trong nhật ký.
- Nếu ví dụ cần dữ liệu, chỉ dùng dữ liệu giả lập hoặc đã khử định danh.

[Output Requirements]

Tạo mẫu nhật ký có thể dùng trong Markdown hoặc bảng tính.

[Output Format]

Trả về:

1. Bảng Markdown với các cột: Ngày, Giai đoạn SDLC, Mục tiêu, Prompt đã dùng, Công cụ AI, Tóm tắt phản hồi, Cách kiểm chứng, Chỉnh sửa của sinh viên, Kết quả, Ghi chú bảo mật.
2. 3 dòng ví dụ đã điền cho:
   - Phân tích use case đặt lịch khám.
   - Sinh API CRUD quản lý dịch vụ nha khoa.
   - Debug lỗi cập nhật tồn kho vật tư.
3. Hướng dẫn ngắn cách dùng nhật ký khi nộp bài, nhấn mạnh sinh viên cần tự kiểm chứng đầu ra AI và không ghi dữ liệu bệnh nhân thật.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `01-Vi-du-prompt.md` thì file kết quả phải là `01-Vi-du-prompt_ket_qua.md`.
