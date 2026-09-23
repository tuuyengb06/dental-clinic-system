# Prompt: Thiết kế prompt template tái sử dụng cho Hệ thống Nha khoa

## Kỹ thuật minh họa
Prompt Template & Parameterization: Tái sử dụng cấu trúc prompt tiêu chuẩn bằng cách sử dụng các biến giữ chỗ (placeholders) để đảm bảo tính nhất quán, an toàn dữ liệu y tế và tối ưu hóa quy trình phát triển phần mềm (SDLC).

## Prompt sử dụng

[Instructions]
Thiết kế một prompt template chuẩn có khả năng tái sử dụng cao dành cho đội ngũ phát triển (BA, Developer, QA) thuộc dự án Hệ thống Quản lý Phòng khám Nha khoa Tích hợp AI.

[Context]
- Template được sử dụng xuyên suốt vòng đời phát triển phần mềm (SDLC): phân tích yêu cầu nghiệp vụ y tế, thiết kế CSDL (vật tư, EMR, lịch hẹn), sinh API CRUD, sinh QA test case, debug lỗi thuật toán/database và viết tài liệu kỹ thuật.
- Tech Stack của dự án: Backend FastAPI/Python, Frontend React/TypeScript, Database PostgreSQL (lưu trữ EMR, Dental Chart), VectorDB (ChromaDB/Qdrant cho RAG Chatbot), AI Framework (LangChain/LlamaIndex).
- Đặc thù an toàn thông tin y tế: Prompt template bắt buộc phải ngăn chặn việc gửi dữ liệu nhạy cảm của bệnh nhân (PHI/PII như Số CMND/CCCD, Số điện thoại, Tiền sử bệnh lý thực tế, Ảnh chụp X-quang định danh) hoặc thông tin hệ thống bảo mật (Database Credentials, JWT Secret Key, API Key).

[Input Data / Constraints]
- Cấu trúc Template bắt buộc bao gồm các trường chuẩn: `[Vai trò]`, `[Bối cảnh dự án]`, `[Nhiệm vụ cụ thể]`, `[Đầu vào / Context]`, `[Ràng buộc kỹ thuật & Y tế]`, `[Tiêu chí đánh giá]`, `[Định dạng đầu ra]`.
- Sử dụng chuẩn placeholder cú pháp `{{ten_truong}}`.
- Cung cấp hướng dẫn ngắn gọn, dễ hiểu về nguyên tắc điền từng trường cho thành viên dự án.
- Thiết kế đảm bảo tính linh hoạt, không quá cồng kềnh nhưng đầy đủ các ràng buộc an toàn y tế y khoa.

[Output Format]
Trình bày tài liệu Markdown gồm các phần:
1. **Prompt Template chuẩn (Production-ready)** đặt trong khối code block Markdown.
2. **Bảng hướng dẫn chi tiết ý nghĩa & quy tắc điền các Placeholder**.
3. **Ví dụ thực tế (Sample Execution)**: Một ví dụ minh họa hoàn chỉnh đã điền thông tin cụ thể cho tác vụ *"Sinh RESTful API CRUD Quản lý Hồ sơ Bệnh án Điện tử (EMR) & Sơ đồ răng (Dental Chart)"*.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `35-Thiet-ke-prompt-template-tai-su-dung-nha-khoa.md` thì file kết quả phải là `35-Thiet-ke-prompt-template-tai-su-dung-nha-khoa_ket_qua.md`.