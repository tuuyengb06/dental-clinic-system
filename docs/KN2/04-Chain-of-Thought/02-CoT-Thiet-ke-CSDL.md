# Prompt: Thiết kế CSDL bằng Chain-of-Thought

## Kỹ thuật minh họa

Phân tích bài toán theo nhiều khía cạnh và cân nhắc quan hệ dữ liệu trước khi đề xuất lược đồ.

## Prompt sử dụng

Bạn là kiến trúc sư cơ sở dữ liệu. Hãy thiết kế CSDL cho hệ thống quản lý nha khoa có tích hợp AI.

Ngữ cảnh:

- Cần quản lý người dùng, vai trò, bệnh nhân, lịch hẹn, hồ sơ khám, dịch vụ nha khoa, kế hoạch điều trị, hóa đơn, chi tiết hóa đơn, thanh toán và vật tư.
- Cần hỗ trợ báo cáo hoạt động và doanh thu theo ngày, tháng, dịch vụ hoặc các tiêu chí phù hợp.
- Cần cung cấp cho chatbot nội dung dịch vụ và thông tin lịch hẹn cần thiết để trả lời câu hỏi thường gặp.
- AI có thể hỗ trợ tóm tắt thông tin khám hoặc tạo nhận xét từ dữ liệu tổng hợp; nội dung chuyên môn phải được bác sĩ xem xét trước khi sử dụng.
- Dữ liệu sức khỏe và thông tin định danh bệnh nhân cần được bảo vệ theo quyền truy cập.

Hãy phân tích các khía cạnh sau và trình bày kết luận, quyết định thiết kế cùng các giả định cần xác minh:

1. Xác định các entity chính.
2. Xác định thuộc tính quan trọng của từng entity.
3. Xác định khóa chính, khóa ngoại.
4. Xác định quan hệ 1-n, n-n nếu có.
5. Xác định ràng buộc dữ liệu để bảo đảm tính nhất quán của lịch hẹn, hồ sơ khám, hóa đơn, thanh toán và vật tư.
6. Đề xuất lược đồ bảng.

Ràng buộc:

- Ưu tiên SQLite cho bản demo.
- Không lưu API key trong CSDL.
- Không thiết kế để gửi dữ liệu định danh hoặc hồ sơ sức khỏe đến AI nếu không cần thiết; ưu tiên dữ liệu tối thiểu hoặc đã khử định danh.
- Không giả định quy định nghiệp vụ chưa nêu, chẳng hạn quy trình hoàn tiền, hủy hóa đơn, thời điểm trừ vật tư hoặc thời hạn lưu hồ sơ. Ghi rõ các giả định và câu hỏi cần xác nhận.
- Phân biệt dữ liệu hồ sơ bệnh nhân với dữ liệu tổng hợp phục vụ báo cáo.
- Đề xuất cách thể hiện quyền truy cập của người dùng, nhưng không đưa thông tin xác thực hoặc bí mật vào ví dụ.
- Không đưa ra chẩn đoán hoặc khuyến nghị điều trị thay cho bác sĩ.

Định dạng đầu ra:

1. Danh sách entity và lý do tồn tại.
2. Bảng thiết kế CSDL dạng Markdown, gồm tên bảng, cột, kiểu dữ liệu, khóa và ràng buộc chính.
3. Mô tả các quan hệ.
4. Gợi ý chỉ mục phục vụ tra cứu và báo cáo.
5. Mermaid ERD.
6. Các giả định và điểm cần xác minh với phòng khám.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `01-Vi-du-prompt.md` thì file kết quả phải là `01-Vi-du-prompt_ket_qua.md`.
