# Prompt: Xác định actor và chức năng bằng Zero-Shot

## Kỹ thuật minh họa

Zero-Shot Prompting: yêu cầu trực tiếp, không cung cấp ví dụ mẫu.

## Prompt sử dụng

Bạn là chuyên viên phân tích hệ thống. Dựa trên mô tả sau, hãy xác định actor và chức năng chính cho hệ thống quản lý nha khoa có tích hợp AI.

Bối cảnh:

- Phòng khám nha khoa cần quản lý bệnh nhân, lịch hẹn, hồ sơ khám, dịch vụ, kế hoạch điều trị, hóa đơn, thanh toán, vật tư và báo cáo.
- Người dùng gồm quản trị viên, lễ tân, bác sĩ nha khoa, phụ tá nha khoa và chủ phòng khám.
- Hệ thống có các chức năng quản lý: đăng nhập, phân quyền, quản lý hồ sơ bệnh nhân, quản lý lịch hẹn, ghi nhận thông tin khám, quản lý dịch vụ nha khoa, lập kế hoạch điều trị, lập hóa đơn, ghi nhận thanh toán, theo dõi vật tư, tìm kiếm/lọc và xem hoặc xuất báo cáo.
- Hệ thống có chức năng AI: chatbot trả lời câu hỏi thường gặp về dịch vụ và lịch hẹn; hỗ trợ tóm tắt thông tin khám hoặc soạn thảo nội dung để bác sĩ xem xét; hỏi đáp dữ liệu hoạt động của phòng khám bằng ngôn ngữ tự nhiên theo quyền truy cập.
- AI chỉ hỗ trợ; không tự chẩn đoán hoặc quyết định điều trị thay bác sĩ.

Yêu cầu:

1. Liệt kê các actor được nêu trong bối cảnh.
2. Với mỗi actor, liệt kê các chức năng phù hợp dựa trên mô tả đã cho.
3. Chỉ ra chức năng và loại dữ liệu nào cần phân quyền chặt chẽ, đặc biệt là hồ sơ sức khỏe, thông tin bệnh nhân và nội dung do AI hỗ trợ tạo.
4. Nêu rõ chức năng AI nào cần bác sĩ hoặc nhân viên có thẩm quyền xem xét trước khi sử dụng.
5. Không tự thêm actor hoặc chức năng ngoài bối cảnh trên. Nếu quyền hạn của actor chưa được xác định, ghi rõ là cần làm rõ thay vì tự suy đoán.

Định dạng đầu ra:

- Bảng actor - mục tiêu - chức năng.
- Danh sách chức năng và dữ liệu cần bảo vệ quyền truy cập.
- Danh sách đầu ra AI cần được nhân viên có thẩm quyền xem xét.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `01-Vi-du-prompt.md` thì file kết quả phải là `01-Vi-du-prompt_ket_qua.md`.
