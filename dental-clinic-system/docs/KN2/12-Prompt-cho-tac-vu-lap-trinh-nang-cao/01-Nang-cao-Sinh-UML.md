# Prompt: Sinh sơ đồ UML cho Hệ thống Quản lý Phòng khám Nha khoa Tích hợp AI

## Kỹ thuật minh họa
Prompt cho tác vụ thiết kế kiến trúc phần mềm nâng cao: Sinh sơ đồ UML (Use Case Diagram & Class Diagram) bằng cú pháp Mermaid để dễ dàng nhúng vào tài liệu Markdown.

## Prompt sử dụng

[Instructions]
Tạo sơ đồ UML bằng cú pháp Mermaid cho "Hệ thống Quản lý Phòng khám Nha khoa Tích hợp AI" (Dental Clinic Management System with Integrated AI).

[Context]
- Hệ thống phục vụ các Actors chính: Quản trị viên hệ thống (Admin), Bác sĩ Nha khoa (Dentist), Lễ tân / Thu ngân (Receptionist), và Bệnh nhân (Patient).
- Các phân hệ quản lý chính: Đăng nhập/Xác thực & Phân quyền (Auth/RBAC), Quản lý Hồ sơ Bệnh nhân (Patient EMR & Dental Chart - Sơ đồ răng), Quản lý Lịch hẹn & Nhắc lịch (Appointments), Lập Hóa đơn & Kế hoạch Trả góp (Invoices & Installments), Quản lý Vật tư Y tế & Tồn kho (Medical Supplies & Inventory), Báo cáo Doanh thu & Hiệu suất Phòng khám (Reports).
- Các phân hệ AI tích hợp: 
  1. AI Chatbot 24/7 tư vấn dịch vụ & hỗ trợ đặt lịch khám.
  2. AI phân tích ảnh X-quang nha khoa hỗ trợ chẩn đoán (X-ray Diagnostic Assistant).
  3. AI Agent hỏi đáp dữ liệu phòng khám (NL2SQL Agent) & tự động sinh nhận xét báo cáo doanh thu, dự báo tồn kho vật tư y tế.

[Tasks]
1. Tạo sơ đồ **Use Case Diagram** bằng cú pháp Mermaid mô tả tương tác giữa các Actors và các chức năng hệ thống (bao gồm cả tính năng AI).
2. Tạo sơ đồ **Class Diagram** bằng cú pháp Mermaid cho các thực thể dữ liệu chính: `User`, `Role`, `Patient`, `DentalChart`, `Appointment`, `DentalService`, `MedicalSupply`, `Invoice`, `InvoiceDetail`, `XrayAnalysis`, và `AIReportInsight`.
3. Giải thích ngắn gọn bằng tiếng Việt về mối quan hệ giữa các lớp chính và luồng xử lý của phân hệ AI.

[Constraints]
- Chỉ tập trung vào phạm vi nghiệp vụ phòng khám nha khoa đã nêu, không thêm các module bán hàng ngoài luồng.
- Tên các Class, thuộc tính (Attributes) và phương thức (Methods) sử dụng tiếng Anh chuẩn để thuận tiện cho việc thiết kế CSDL và triển khai mã nguồn (OOP).

[Output Format]
Trình bày bằng Markdown bao gồm:
1. Đoạn mã Mermaid cho Use Case Diagram.
2. Đoạn mã Mermaid cho Class Diagram.
3. Giải thích ngắn gọn bằng tiếng Việt về quan hệ giữa các lớp và điểm nhấn tích hợp AI.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `26-Sinh-uml-he-thong-nha-khoa.md` thì file kết quả phải là `26-Sinh-uml-he-thong-nha-khoa_ket_qua.md`.