# Prompt: Phân tích yêu cầu hệ thống quản lý nha khoa tích hợp AI

## Kỹ thuật minh họa

Cấu trúc prompt hiệu quả: Instructions, Context, Input Data/Constraints, Examples, Output Format.

## Prompt sử dụng

[Instructions]

Dựa vào mô tả bài toán: `Codes\Bai 03\project.md`.

Phân tích yêu cầu cho hệ thống quản lý nha khoa tích hợp AI. Hãy xác định vấn đề nghiệp vụ, mục tiêu, actor, chức năng chính, dữ liệu chính, yêu cầu phi chức năng và các rủi ro cần lưu ý.

[Context]

- Bạn là chuyên viên phân tích nghiệp vụ phần mềm.
- Hệ thống được sử dụng tại phòng khám nha khoa.
- Hệ thống cần hỗ trợ quản lý bệnh nhân, lịch hẹn, hồ sơ khám, dịch vụ nha khoa, kế hoạch điều trị, hóa đơn, thanh toán, vật tư và báo cáo.
- Các chức năng AI dự kiến gồm:
  - Chatbot trả lời câu hỏi thường gặp về dịch vụ nha khoa, quy trình đặt lịch và hướng dẫn chuẩn bị trước/sau khi khám dựa trên nội dung đã được phòng khám phê duyệt.
  - AI hỗ trợ tóm tắt thông tin khám và soạn thảo ghi chú hoặc kế hoạch điều trị để bác sĩ xem xét.
  - Hỏi đáp dữ liệu hoạt động của phòng khám bằng ngôn ngữ tự nhiên, theo quyền truy cập của người dùng.

[Input Data / Constraints]

- Chỉ dựa trên mô tả sau và tài liệu `Codes\Bai 03\project.md`, không tự thêm nghiệp vụ mâu thuẫn. Nếu tài liệu không cung cấp đủ thông tin, hãy ghi rõ là giả định hoặc điểm cần kiểm chứng.
- Người dùng gồm quản trị viên, lễ tân, bác sĩ nha khoa, phụ tá nha khoa và chủ phòng khám. Nếu tài liệu nguồn quy định actor khác, hãy ưu tiên tài liệu nguồn và nêu điểm khác biệt.
- Hồ sơ bệnh nhân có thể gồm mã bệnh nhân, thông tin liên hệ, lịch sử khám, tiền sử bệnh do bệnh nhân cung cấp và lịch sử điều trị.
- Lịch hẹn cần quản lý thông tin bệnh nhân, thời gian, nhu cầu hoặc dịch vụ khám, nhân viên phụ trách và trạng thái lịch hẹn.
- Hồ sơ khám có thể gồm tình trạng răng, ghi chú chuyên môn, dịch vụ đã thực hiện và kế hoạch điều trị.
- Dịch vụ nha khoa có mã, tên, mô tả, giá và trạng thái hoạt động.
- Hóa đơn cần ghi nhận các dịch vụ, số lượng, giảm giá nếu có, tổng tiền và phương thức thanh toán.
- Vật tư nha khoa cần được theo dõi thông tin cơ bản như mã, tên, đơn vị tính, số lượng tồn và trạng thái. Chỉ mô tả nghiệp vụ nhập, xuất hoặc kiểm kê nếu có trong tài liệu nguồn.
- Báo cáo có thể liên quan đến lịch hẹn, lượt khám, doanh thu, dịch vụ được sử dụng và tình hình vật tư; chỉ xác định chi tiết dựa trên tài liệu nguồn.
- AI chỉ hỗ trợ cung cấp thông tin hoặc soạn thảo; không được tự đưa ra chẩn đoán, chỉ định điều trị hay cam kết kết quả thay bác sĩ.
- Nội dung chuyên môn do AI tạo ra phải được bác sĩ hoặc nhân viên có thẩm quyền xem xét và xác nhận trước khi sử dụng.
- Khi gửi dữ liệu đến AI, không gửi thông tin định danh hoặc dữ liệu sức khỏe nếu không cần thiết; ưu tiên giảm thiểu hoặc khử định danh dữ liệu.
- Hệ thống cần phân quyền truy cập theo vai trò; không giả định mọi người dùng đều được xem toàn bộ hồ sơ bệnh nhân.
- Nêu các yêu cầu về bảo mật, quyền riêng tư, sự đồng ý của bệnh nhân, lưu trữ và xử lý dữ liệu sức khỏe nếu tài liệu nguồn chưa quy định; đánh dấu rõ các nội dung cần xác nhận, không tự khẳng định là yêu cầu pháp lý cụ thể.

[Examples]

Ví dụ cách diễn đạt actor:

- Actor: Lễ tân
- Mục tiêu: Đặt và cập nhật lịch hẹn, tra cứu thông tin cần thiết của bệnh nhân và hỗ trợ tiếp nhận bệnh nhân.
- Chức năng liên quan: Tìm hồ sơ bệnh nhân theo quyền hạn, tạo lịch hẹn, cập nhật trạng thái lịch hẹn và chuyển thông tin cần thiết cho bác sĩ.

[Output Format]

Trả lời bằng Markdown với các mục:

1. Bối cảnh và vấn đề
2. Mục tiêu hệ thống
3. Actor và nhu cầu
4. Danh sách chức năng quản lý
5. Danh sách chức năng AI
6. Dữ liệu chính
7. Yêu cầu phi chức năng
8. Rủi ro và giả định cần kiểm chứng

Với mỗi chức năng, mô tả ngắn gọn mục tiêu và actor liên quan. Phân biệt rõ nội dung có trong tài liệu nguồn với giả định hoặc điểm cần làm rõ; không trình bày giả định như yêu cầu đã được xác nhận.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả phân tích vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `01-Vi-du-prompt.md` thì file kết quả phải là `01-Vi-du-prompt_ket_qua.md`.
