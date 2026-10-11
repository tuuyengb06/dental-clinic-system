# Prompt: Thiết kế prompt template tái sử dụng cho hệ thống nha khoa tích hợp AI

## Kỹ thuật minh họa

Prompt template: tái sử dụng prompt với placeholder để đảm bảo nhất quán.

## Prompt sử dụng

[Instructions]

Thiết kế một prompt template tái sử dụng cho nhóm sinh viên phát triển hệ thống quản lý nha khoa có tích hợp AI.

[Context]

- Template dùng để yêu cầu AI hỗ trợ các tác vụ trong SDLC: phân tích yêu cầu, thiết kế CSDL, sinh API CRUD, sinh test case, debug và viết tài liệu.
- Dự án quản lý phòng khám nha khoa, có thể gồm các nghiệp vụ như bệnh nhân, lịch hẹn, hồ sơ khám, dịch vụ nha khoa, kế hoạch điều trị, hóa đơn, thanh toán, vật tư và báo cáo.
- Backend có thể dùng Python FastAPI/Flask/Django; frontend có thể dùng React/Vue/HTML/CSS/JavaScript; CSDL có thể dùng SQLite/MySQL/PostgreSQL.
- AI trong hệ thống chỉ có vai trò hỗ trợ. Nội dung liên quan đến chẩn đoán hoặc điều trị phải được bác sĩ có thẩm quyền xem xét; AI không được thay thế quyết định chuyên môn của bác sĩ.
- Prompt template cần giúp sinh viên cung cấp đủ ngữ cảnh nhưng tránh gửi dữ liệu nhạy cảm như thông tin định danh bệnh nhân, số điện thoại đầy đủ, hồ sơ sức khỏe chi tiết, dữ liệu thanh toán hoặc API key.

[Input Data / Constraints]

- Template phải có các trường: [Vai trò], [Bối cảnh dự án], [Nhiệm vụ], [Đầu vào], [Ràng buộc], [Tiêu chí đạt], [Định dạng đầu ra].
- Dùng placeholder dạng `{{ten_truong}}`.
- Có hướng dẫn ngắn về cách điền từng trường.
- Không tạo template quá dài hoặc khó dùng.
- Nội dung template phải nhắc AI không tự bịa thông tin còn thiếu; cần nêu giả định hoặc hỏi lại khi thiếu dữ liệu quan trọng.
- Không yêu cầu người dùng cung cấp dữ liệu thật có thể nhận diện bệnh nhân. Dùng dữ liệu giả lập hoặc đã khử định danh trong ví dụ.

[Output Format]

Trả về:

1. Prompt template hoàn chỉnh trong khối code Markdown.
2. Bảng giải thích từng placeholder.
3. Một ví dụ đã điền template cho tác vụ “sinh API CRUD quản lý dịch vụ nha khoa”.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `01-Vi-du-prompt.md` thì file kết quả phải là `01-Vi-du-prompt_ket_qua.md`.
