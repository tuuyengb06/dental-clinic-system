# Prompt: Viết README dự án quản lý nha khoa tích hợp AI

## Kỹ thuật minh họa

Prompt viết tài liệu: yêu cầu rõ cấu trúc, đối tượng đọc và phạm vi.

## Prompt sử dụng

[Instructions]

Viết file `README.md` cho dự án hệ thống quản lý nha khoa có tích hợp AI.

[Context]

- Đối tượng đọc là giảng viên, sinh viên trong nhóm và người muốn chạy bản demo.
- Hệ thống quản lý bệnh nhân, lịch hẹn, hồ sơ khám, dịch vụ nha khoa, kế hoạch điều trị, hóa đơn, thanh toán, vật tư và báo cáo.
- Chức năng AI gồm chatbot cung cấp thông tin dịch vụ dựa trên nội dung đã được phòng khám phê duyệt, hỗ trợ tóm tắt thông tin khám để bác sĩ xem xét và hỏi đáp dữ liệu hoạt động tổng hợp theo quyền truy cập.
- Backend có thể dùng FastAPI/Flask/Django; frontend có thể dùng React/Vue/HTML/CSS/JavaScript; CSDL demo có thể dùng SQLite.
- Nếu tài liệu dự án chưa xác định công nghệ hoặc lệnh chạy cụ thể, hãy dùng placeholder rõ ràng hoặc đánh dấu cần bổ sung; không tự khẳng định cấu hình chưa được cung cấp.

[Constraints]

- Không ghi API key hoặc thông tin xác thực thật.
- Có mục cấu hình `.env` và `.env.example`; chỉ ghi tên biến và giá trị minh họa giả.
- Có hướng dẫn cài đặt và chạy local; phân biệt lệnh đã được xác nhận với lệnh placeholder cần thay theo dự án.
- Có dữ liệu mẫu và tài khoản demo dạng giả định; không dùng thông tin bệnh nhân thật.
- Có mục hướng dẫn chạy kiểm thử.
- Có mục lưu ý bảo mật khi gọi AI: giảm thiểu dữ liệu, không gửi thông tin định danh hoặc hồ sơ sức khỏe nếu không cần, kiểm soát quyền truy cập.
- Làm rõ AI chỉ hỗ trợ; không thay thế bác sĩ trong chẩn đoán hoặc quyết định điều trị, và nội dung chuyên môn do AI tạo cần được người có thẩm quyền xem xét.
- Không mô tả chức năng, công nghệ hoặc quy trình như đã triển khai nếu nguồn thông tin không xác nhận.

[Output Format]

README Markdown gồm:

1. Tên dự án
2. Mô tả ngắn
3. Chức năng quản lý chính
4. Chức năng AI và giới hạn sử dụng
5. Công nghệ sử dụng
6. Cấu trúc thư mục đề xuất
7. Cài đặt và chạy local
8. Cấu hình môi trường
9. Dữ liệu mẫu và tài khoản demo
10. Kiểm thử
11. Lưu ý bảo mật và quyền riêng tư

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `01-Vi-du-prompt.md` thì file kết quả phải là `01-Vi-du-prompt_ket_qua.md`.
