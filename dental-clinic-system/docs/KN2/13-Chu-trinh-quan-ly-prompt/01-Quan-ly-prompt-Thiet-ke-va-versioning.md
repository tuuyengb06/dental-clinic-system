# Prompt: Quản lý prompt bằng versioning và catalog cho hệ thống nha khoa tích hợp AI

## Kỹ thuật minh họa
Prompt Management Cycle: Design, Testing & Evaluation, Refinement, Versioning & Cataloging, Deployment, Monitoring & Iteration. Áp dụng quy trình quản lý prompt chuyên nghiệp, minh bạch và có khả năng truy xuất nguồn gốc (traceability) cho dự án phần mềm y tế.

## Prompt sử dụng

[Instructions]
Thiết kế quy trình quản lý, phân bản (versioning) và danh mục catalog cho toàn bộ các prompt AI trong Hệ thống Quản lý Phòng khám Nha khoa Tích hợp AI.

[Context]
- Các prompt AI trong hệ thống nha khoa bao gồm: Chatbot tư vấn dịch vụ & đặt lịch khám, AI hỗ trợ phân tích ảnh X-quang, AI sinh nhận xét báo cáo doanh thu & tồn kho vật tư y tế, và NL2SQL Agent hỏi đáp dữ liệu phòng khám.
- Đặc thụ ngành Y tế: Cần kiểm soát chặt chẽ an toàn thông tin bệnh nhân (PHI/PII), tránh việc AI tư vấn sai liều lượng/phác đồ, tránh bịa đặt giá dịch vụ, và ngăn chặn hành vi kê đơn thuốc trái thẩm quyền.
- Đội ngũ phát triển (Kỹ sư phần mềm, Bác sĩ cố vấn chuyên môn, Tester) cần lưu trữ toàn bộ prompt trong Git repository để phục vụ đánh giá nghiệm thu, kiểm toán chất lượng và rollback khi có sự cố.

[Tasks]
1. Đề xuất cấu trúc thư mục lưu trữ prompt catalog chuẩn hóa trong mã nguồn dự án.
2. Thiết kế mẫu Metadata (YAML/JSON) cho mỗi tệp prompt (bao gồm các trường kiểm soát an toàn y tế).
3. Mô tả chi tiết quy trình 6 giai đoạn quản lý vòng đời prompt (Prompt Management Life Cycle).
4. Đề xuất quy tắc đánh số phiên bản Semantic Versioning (v1.0.0, v1.1.0, v2.0.0) dành riêng cho Prompt Engineering.
5. Xây dựng Checklist kiểm thử an toàn & chất lượng trước khi đưa prompt vào môi trường Production.
6. Cung cấp ví dụ Changelog theo dõi lịch sử cải tiến của prompt Chatbot Nha khoa.

[Output Format]
Trình bày file Markdown gồm các phần:
1. Cấu trúc thư mục Prompt Catalog.
2. Bảng Metadata tiêu chuẩn của tệp Prompt.
3. Quy trình 6 giai đoạn Vòng đời Prompt (Prompt Lifecycle).
4. Quy tắc Versioning và Đánh dấu trạng thái (Draft, Staging, Production, Deprecated).
5. Checklist triển khai (Deployment Checklist).
6. Mẫu Changelog thực tế cho Chatbot Nha khoa.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ nếu file prompt là `28-Quan-ly-prompt-bang-versioning-catalog-nha-khoa.md` thì file kết quả phải là `28-Quan-ly-prompt-bang-versioning-catalog-nha-khoa_ket_qua.md`.