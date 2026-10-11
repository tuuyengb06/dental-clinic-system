# Prompt: Phân loại yêu cầu bằng Few-Shot

## Kỹ thuật minh họa

Few-Shot Prompting: cung cấp ví dụ để mô hình học cách phân loại.

## Prompt sử dụng

Bạn là chuyên viên phân tích yêu cầu. Hãy phân loại các yêu cầu của hệ thống quản lý nha khoa tích hợp AI thành một trong bốn nhóm:

- Quản lý dữ liệu
- Nghiệp vụ khám chữa bệnh
- Báo cáo/Thống kê
- Chức năng AI

Chọn nhóm thể hiện mục đích chính của mỗi yêu cầu. Nếu yêu cầu có thể thuộc nhiều nhóm, hãy chọn nhóm phù hợp nhất và giải thích ngắn gọn.

Ví dụ:

Input: "Lễ tân có thể thêm, cập nhật và ngừng sử dụng hồ sơ dịch vụ nha khoa."
Output: Quản lý dữ liệu

Input: "Bác sĩ ghi nhận kết quả khám và lập kế hoạch điều trị cho bệnh nhân."
Output: Nghiệp vụ khám chữa bệnh

Input: "Chủ phòng khám xem tổng doanh thu theo tháng và dịch vụ được sử dụng nhiều nhất."
Output: Báo cáo/Thống kê

Input: "AI hỗ trợ tóm tắt ghi chú khám để bác sĩ xem xét và xác nhận."
Output: Chức năng AI

Hãy phân loại các yêu cầu sau:

1. Quản trị viên tạo tài khoản nhân viên và gán vai trò truy cập.
2. Lễ tân tạo lịch hẹn và cập nhật trạng thái khi bệnh nhân đến khám.
3. AI tóm tắt thông tin khám để bác sĩ kiểm tra trước khi lưu vào hồ sơ.
4. Chủ phòng khám lọc hóa đơn theo khoảng thời gian và trạng thái thanh toán.
5. Hệ thống cập nhật số lượng vật tư sau khi ghi nhận sử dụng trong quá trình điều trị.
6. Chủ phòng khám hỏi chatbot: "Tháng này dịch vụ nha khoa nào được sử dụng nhiều nhất?"

Định dạng đầu ra:

Bảng Markdown gồm: STT, Yêu cầu, Nhóm, Giải thích ngắn.

Không tự thêm nhóm phân loại hoặc thay đổi nội dung các yêu cầu. Với các chức năng AI có nội dung chuyên môn, lưu ý rằng kết quả AI cần được bác sĩ hoặc nhân viên có thẩm quyền xem xét; không xem AI là bên tự chẩn đoán hoặc quyết định điều trị.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `01-Vi-du-prompt.md` thì file kết quả phải là `01-Vi-du-prompt_ket_qua.md`.
