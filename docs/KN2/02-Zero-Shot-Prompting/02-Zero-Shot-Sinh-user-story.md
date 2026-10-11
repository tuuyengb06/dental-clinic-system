# Prompt: Sinh User Story bằng Zero-Shot

## Kỹ thuật minh họa

Zero-Shot Prompting cho tác vụ phổ biến, có cấu trúc đầu ra rõ ràng.

## Prompt sử dụng

Hãy viết user story cho hệ thống quản lý nha khoa có tích hợp AI.

Ngữ cảnh hệ thống:

- Lễ tân cần tiếp nhận bệnh nhân, tra cứu thông tin cần thiết theo quyền hạn, tạo và cập nhật lịch hẹn.
- Bác sĩ nha khoa cần xem hồ sơ khám theo quyền hạn, ghi nhận thông tin khám, lập kế hoạch điều trị và xác nhận nội dung chuyên môn.
- Phụ tá nha khoa cần hỗ trợ cập nhật thông tin phục vụ quá trình khám và điều trị theo phân quyền.
- Chủ phòng khám cần xem báo cáo hoạt động và doanh thu theo các tiêu chí hệ thống cung cấp.
- Quản trị viên cần quản lý người dùng, vai trò và cấu hình hệ thống.
- Chatbot AI chỉ trả lời câu hỏi thường gặp về dịch vụ và lịch hẹn dựa trên nội dung đã được phòng khám phê duyệt.
- AI có thể hỗ trợ tóm tắt thông tin khám hoặc soạn thảo nội dung để bác sĩ xem xét; AI không tự chẩn đoán hoặc quyết định điều trị thay bác sĩ.

Yêu cầu:

- Viết 10 user story quan trọng nhất dựa trên ngữ cảnh hệ thống.
- Mỗi user story dùng mẫu: “Là một [actor], tôi muốn [mục tiêu] để [lợi ích].”
- Mỗi user story có từ 2 đến 4 tiêu chí chấp nhận, diễn đạt rõ ràng và có thể kiểm thử.
- Không đưa vào chức năng ngoài phạm vi quản lý nha khoa đã mô tả.
- Với chức năng liên quan dữ liệu bệnh nhân, phải thể hiện việc truy cập theo phân quyền.
- Với nội dung chuyên môn do AI hỗ trợ tạo, phải yêu cầu bác sĩ xem xét và xác nhận trước khi sử dụng.
- Không yêu cầu đưa thông tin định danh hoặc hồ sơ sức khỏe thật của bệnh nhân vào user story.
- Nếu thông tin về quyền hạn hoặc quy tắc nghiệp vụ chưa đủ rõ, ghi nhận là điểm cần xác nhận thay vì tự đặt thêm quy tắc.

Định dạng đầu ra: Markdown, mỗi user story gồm:

- Mã: US-xx
- User story
- Tiêu chí chấp nhận

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `01-Vi-du-prompt.md` thì file kết quả phải là `01-Vi-du-prompt_ket_qua.md`.
