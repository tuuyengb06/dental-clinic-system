# Prompt: Sinh UML cho hệ thống quản lý nha khoa

## Kỹ thuật minh họa

Prompt cho tác vụ phân tích và thiết kế hệ thống: sinh sơ đồ UML bằng Mermaid.

## Prompt sử dụng

[Instructions]

Tạo sơ đồ UML dạng Mermaid cho hệ thống quản lý nha khoa có tích hợp AI.

[Context]

- Hệ thống có các actor: quản trị viên, lễ tân, bác sĩ nha khoa, phụ tá nha khoa và chủ phòng khám.
- Chức năng quản lý: đăng nhập, phân quyền, quản lý bệnh nhân, lịch hẹn, hồ sơ khám, dịch vụ nha khoa, kế hoạch điều trị, hóa đơn, thanh toán, vật tư, báo cáo và xuất file.
- Chức năng AI: chatbot cung cấp thông tin dịch vụ dựa trên nội dung phòng khám đã phê duyệt, hỗ trợ tóm tắt thông tin khám để bác sĩ xem xét, và hỏi đáp dữ liệu hoạt động tổng hợp theo quyền truy cập.
- AI không tự chẩn đoán hoặc quyết định điều trị thay bác sĩ.

[Tasks]

1. Tạo Use Case Diagram bằng Mermaid.
2. Tạo Class Diagram bằng Mermaid cho các lớp chính, có thể gồm: `User`, `Role`, `Patient`, `Appointment`, `DentalService`, `TreatmentRecord`, `TreatmentPlan`, `Invoice`, `InvoiceItem`, `Payment`, `InventoryItem`, `InventoryMovement`, `AIRequest` và `AIReportRequest`.
3. Giải thích ngắn gọn các quan hệ chính giữa actor, use case và lớp.

[Constraints]

- Không thêm module ngoài phạm vi dự án.
- Tên lớp, thuộc tính và quan hệ trong sơ đồ dùng tiếng Anh để phù hợp khi triển khai code.
- Tên actor và phần giải thích có thể dùng tiếng Việt.
- Thể hiện phân quyền truy cập hồ sơ bệnh nhân và hồ sơ khám theo vai trò.
- Thể hiện việc bác sĩ xem xét/xác nhận nội dung chuyên môn do AI hỗ trợ tạo.
- Không mô hình hóa AI như actor có quyền tự chẩn đoán, quyết định điều trị hoặc tự cập nhật hồ sơ bệnh nhân.
- Chỉ đưa vào lớp và thuộc tính cần thiết cho phạm vi mô tả; nếu có giả định, ghi rõ trong phần giải thích.

[Output Format]

Trả về:

1. Mermaid Use Case Diagram trong khối code.
2. Mermaid Class Diagram trong khối code.
3. Giải thích ngắn bằng tiếng Việt về các quan hệ và giả định chính.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `01-Vi-du-prompt.md` thì file kết quả phải là `01-Vi-du-prompt_ket_qua.md`.
