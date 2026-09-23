# Prompt: Tạo nhật ký sử dụng AI cho dự án quản lý nha khoa

## Kỹ thuật minh họa
Prompt Management Cycle trong thực hành: Ghi nhận prompt, phản hồi, đánh giá độc lập, kiểm chứng an toàn dữ liệu y tế và tinh chỉnh mã nguồn.

## Prompt sử dụng

[Instructions]
Tạo mẫu nhật ký sử dụng AI (AI Usage Log) dành cho sinh viên/nhóm phát triển Hệ thống Quản lý Phòng khám Nha khoa Tích hợp AI.

[Context]
- Nhật ký dùng làm minh chứng học thuật và kỹ thuật cho việc ứng dụng Generative AI trong toàn bộ quy trình phát triển phần mềm (SDLC): Phân tích yêu cầu, Thiết kế kiến trúc, Lập trình backend/frontend, Kiểm thử (Testing) và Viết tài liệu.
- Đặc thù y tế: Tuyệt đối **không lưu trữ thông tin nhận dạng bệnh nhân (PHI/PII)**, dữ liệu lâm sàng thực tế, hoặc API Key/mật khẩu trong nhật ký.
- Cần thể hiện rõ vai trò kiểm chứng (Human-in-the-loop) của sinh viên: Kiểm tra tính đúng đắn về chuyên môn nha khoa, độ chính xác thuật toán và tính an toàn bảo mật.

[Output Requirements]
Tạo mẫu nhật ký định dạng Markdown hoàn chỉnh, có thể copy vào báo cáo dự án hoặc lưu trong tệp `AI_USAGE_LOG.md` của Repository.

[Output Format]
Trả về:
1. **Bảng Markdown Nhật ký AI** với đầy đủ các cột: Ngày, Giai đoạn SDLC, Mục tiêu, Prompt đã dùng, Công cụ AI, Tóm tắt phản hồi, Cách kiểm chứng & Đánh giá, Chỉnh sửa của sinh viên, Kết quả cuối cùng, Ghi chú bảo mật & An toàn dữ liệu y tế.
2. **3 dòng ví dụ thực tế đã điền đầy đủ** tương ứng với 3 tác vụ chuyên sâu:
   - *Tác vụ 1 (Phân tích):* Thiết kế Use Case & Luồng xử lý cho AI phân tích ảnh X-quang răng.
   - *Tác vụ 2 (Lập trình):* Sinh API CRUD quản lý Sơ đồ răng (Dental Chart) & Tiền sử dị ứng bệnh nhân.
   - *Tác vụ 3 (Debug/Optimization):* Debug lỗi Race Condition khi trừ tồn kho vật tư nha khoa (thuốc tê, trụ Implant) trong giao dịch đồng thời.
3. **Hướng dẫn ngắn** cách duy trì, kiểm duyệt an toàn PHI/PII và đóng gói nhật ký khi nộp bài đồ án.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `29-Tao-nhat-ky-su-dung-ai-nha-khoa.md` thì file kết quả phải là `29-Tao-nhat-ky-su-dung-ai-nha-khoa_ket_qua.md`.