# Prompt: Sinh User Story bằng Zero-Shot

## Kỹ thuật minh họa
Zero-Shot Prompting cho tác vụ phổ biến, có cấu trúc đầu ra rõ ràng.

## Prompt sử dụng

Hãy viết user story cho hệ thống quản lý phòng khám nha khoa có tích hợp AI.

Ngữ cảnh hệ thống:
- Bệnh nhân cần đặt lịch hẹn khám/tái khám, xem lịch trình điều trị, lịch sử khám và nhận tư vấn/đặt lịch tự động qua Chatbot AI 24/7.
- Lễ tân/Thu ngân cần tiếp đón check-in, quản lý lịch hẹn (đặt/sửa/hủy), tạo hóa đơn và theo dõi công nợ trả góp của bệnh nhân.
- Bác sĩ nha khoa cần xem hồ sơ bệnh án (EMR), cập nhật sơ đồ răng (Dental Chart), kê đơn thuốc, xem lịch sử khám và nhận gợi ý chẩn đoán sơ bộ từ AI qua ảnh X-quang.
- Chủ phòng khám (Quản lý) cần xem báo cáo doanh thu, hiệu suất bác sĩ, kiểm soát tồn kho vật tư y tế và hỏi đáp dữ liệu phòng khám bằng ngôn ngữ tự nhiên qua AI (NL2SQL).
- Quản trị viên cần quản lý người dùng, phân quyền vai trò và cấu hình an toàn thông tin (mã hóa/ẩn danh PII).

Yêu cầu:
- Viết 10 user story quan trọng nhất đại diện cho các phân hệ trên.
- Mỗi user story dùng mẫu: "Là một [actor], tôi muốn [mục tiêu] để [lợi ích]."
- Mỗi user story kèm theo 2-4 tiêu chí chấp nhận (Acceptance Criteria - AC).
- Không đưa vào các chức năng nằm ngoài phạm vi quản lý nha khoa đã mô tả.

Định dạng đầu ra:
Markdown, mỗi user story gồm:
- Mã: US-xx
- User story
- Tiêu chí chấp nhận (dạng bullet points)

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `03-Sinh-user-story-nha-khoa.md` thì file kết quả phải là `03-Sinh-user-story-nha-khoa_ket_qua.md`.