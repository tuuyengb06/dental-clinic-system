# Prompt: Quản lý prompt bằng versioning và catalog

## Kỹ thuật minh họa

Prompt Management Cycle: Design, Testing & Evaluation, Refinement, Versioning & Cataloging, Deployment, Monitoring & Iteration.

## Prompt sử dụng

[Instructions]

Thiết kế quy trình quản lý prompt cho chức năng chatbot cung cấp thông tin dịch vụ nha khoa trong hệ thống quản lý nha khoa tích hợp AI.

[Context]

- Chatbot trả lời dựa trên dữ liệu dịch vụ và nội dung đã được phòng khám phê duyệt.
- Chatbot không được bịa tên dịch vụ, giá, quy trình hoặc thông tin không có trong nguồn truy xuất.
- Chatbot không chẩn đoán, đề xuất phác đồ điều trị hoặc thay thế tư vấn của bác sĩ.
- Khi không đủ dữ liệu để trả lời, chatbot cần nói rõ giới hạn và hướng dẫn khách liên hệ phòng khám hoặc bác sĩ phù hợp.
- Nhóm sinh viên cần lưu prompt trong repository để quản lý thay đổi, kiểm thử và làm minh chứng sử dụng AI.
- Prompt và dữ liệu kiểm thử không được chứa API key, thông tin định danh bệnh nhân hoặc hồ sơ sức khỏe thật.

[Tasks]

1. Đề xuất cấu trúc thư mục trong repository để lưu prompt, metadata, bộ dữ liệu kiểm thử và tài liệu đánh giá.
2. Đề xuất metadata cần có cho mỗi prompt, gồm thông tin nhận dạng, phiên bản, mục đích, nguồn dữ liệu, ràng buộc an toàn và trạng thái phê duyệt.
3. Mô tả quy trình 6 giai đoạn quản lý prompt: Design, Testing & Evaluation, Refinement, Versioning & Cataloging, Deployment, Monitoring & Iteration.
4. Đề xuất cách đặt version `v1.0`, `v1.1`, `v2.0`, nêu loại thay đổi phù hợp với từng mức.
5. Đề xuất checklist trước khi đưa prompt vào ứng dụng, bao gồm kiểm thử bám nguồn, dữ liệu thiếu hoặc mâu thuẫn, nội dung ngoài phạm vi y tế, quyền riêng tư và khả năng quay lui phiên bản.
6. Viết ví dụ changelog cho prompt chatbot cung cấp thông tin dịch vụ nha khoa.

[Output Format]

Trả lời bằng Markdown gồm:

- Cấu trúc thư mục.
- Bảng metadata.
- Quy trình 6 giai đoạn.
- Quy tắc versioning.
- Checklist triển khai.
- Ví dụ changelog cho prompt chatbot.

Ghi rõ các đề xuất là quy trình tham khảo cho dự án; không khẳng định tuân thủ một tiêu chuẩn hoặc quy định pháp lý cụ thể nếu không có căn cứ trong đầu vào.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `01-Vi-du-prompt.md` thì file kết quả phải là `01-Vi-du-prompt_ket_qua.md`.
