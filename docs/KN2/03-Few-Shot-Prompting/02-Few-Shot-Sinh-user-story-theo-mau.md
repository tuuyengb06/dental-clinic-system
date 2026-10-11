# Prompt: Sinh User Story theo mẫu bằng Few-Shot

## Kỹ thuật minh họa

Few-Shot Prompting để kiểm soát phong cách và mức chi tiết của đầu ra.

## Prompt sử dụng

Bạn là Business Analyst. Hãy viết user story cho hệ thống quản lý nha khoa theo đúng phong cách của các ví dụ.

Ví dụ 1:

Chức năng: Quản lý hồ sơ bệnh nhân

User story:

Là một lễ tân, tôi muốn tạo và cập nhật hồ sơ bệnh nhân để lưu trữ thông tin cần thiết phục vụ việc tiếp nhận và đặt lịch.

Tiêu chí chấp nhận:

- Có thể nhập mã bệnh nhân và các thông tin cơ bản theo biểu mẫu được cấp quyền.
- Không cho lưu hồ sơ thiếu các trường bắt buộc.
- Chỉ người dùng được phân quyền mới có thể xem hoặc cập nhật thông tin bệnh nhân.

Ví dụ 2:

Chức năng: Hỗ trợ tóm tắt thông tin khám bằng AI

User story:

Là một bác sĩ nha khoa, tôi muốn AI hỗ trợ tóm tắt ghi chú khám để tiết kiệm thời gian rà soát hồ sơ.

Tiêu chí chấp nhận:

- AI chỉ sử dụng thông tin khám được phép cung cấp cho tác vụ.
- Bác sĩ có thể xem và chỉnh sửa bản tóm tắt trước khi lưu hoặc sử dụng.
- AI không tự đưa ra chẩn đoán hoặc quyết định điều trị; nếu thiếu dữ liệu, phải nêu rõ thay vì tự bịa.

Nhiệm vụ:

Viết user story cho các chức năng sau:

1. Đặt lịch hẹn khám nha khoa.
2. Ghi nhận kết quả khám và kế hoạch điều trị.
3. Lập hóa đơn và ghi nhận thanh toán cho dịch vụ nha khoa.
4. Xem báo cáo doanh thu theo ngày/tháng.
5. Hỏi đáp dữ liệu hoạt động của phòng khám bằng ngôn ngữ tự nhiên.

Định dạng đầu ra:

Với mỗi chức năng, trình bày:

- Chức năng
- User story
- Tiêu chí chấp nhận

Yêu cầu bổ sung:

- Giữ phong cách, độ chi tiết và cấu trúc giống các ví dụ.
- Mỗi user story dùng mẫu: “Là một [actor], tôi muốn [mục tiêu] để [lợi ích].”
- Viết từ 2 đến 4 tiêu chí chấp nhận có thể kiểm thử cho mỗi chức năng.
- Không tự thêm chức năng ngoài danh sách nhiệm vụ.
- Với dữ liệu bệnh nhân, nêu yêu cầu phân quyền phù hợp.
- Với câu trả lời hoặc nội dung chuyên môn do AI hỗ trợ, yêu cầu bác sĩ hoặc nhân viên có thẩm quyền xem xét; không để AI tự chẩn đoán hoặc quyết định điều trị.
- Không sử dụng dữ liệu định danh bệnh nhân thật trong nội dung đầu ra.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `01-Vi-du-prompt.md` thì file kết quả phải là `01-Vi-du-prompt_ket_qua.md`.
