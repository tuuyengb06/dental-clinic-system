# Phân loại yêu cầu bằng Few-Shot

| STT | Yêu cầu | Nhóm | Giải thích ngắn |
|---:|---|---|---|
| 1 | Quản trị viên tạo tài khoản nhân viên và gán vai trò truy cập. | Quản lý dữ liệu | Tạo/quản lý dữ liệu tài khoản và vai trò; phân quyền là mục đích chính. |
| 2 | Lễ tân tạo lịch hẹn và cập nhật trạng thái khi bệnh nhân đến khám. | Nghiệp vụ khám chữa bệnh | Hỗ trợ luồng tiếp nhận và khám, dù lịch hẹn cũng được lưu dưới dạng dữ liệu. |
| 3 | AI tóm tắt thông tin khám để bác sĩ kiểm tra trước khi lưu vào hồ sơ. | Chức năng AI | AI tạo bản tóm tắt; bác sĩ phải kiểm tra, không phải AI tự chẩn đoán hay quyết định. |
| 4 | Chủ phòng khám lọc hóa đơn theo khoảng thời gian và trạng thái thanh toán. | Báo cáo/Thống kê | Trọng tâm là lọc dữ liệu tài chính để theo dõi hoạt động. Quyền xem chi tiết hóa đơn cần được phân quyền. |
| 5 | Hệ thống cập nhật số lượng vật tư sau khi ghi nhận sử dụng trong quá trình điều trị. | Nghiệp vụ khám chữa bệnh | Cập nhật tồn kho phát sinh từ quy trình sử dụng vật tư trong điều trị; quy tắc kho cụ thể cần được xác nhận. |
| 6 | Chủ phòng khám hỏi chatbot: “Tháng này dịch vụ nha khoa nào được sử dụng nhiều nhất?” | Chức năng AI | Người dùng đặt câu hỏi ngôn ngữ tự nhiên qua chatbot; kết quả cần dựa trên dữ liệu tổng hợp và quyền truy cập. |

**Lưu ý:** các yêu cầu có thể chạm nhiều nhóm, bảng chọn nhóm theo mục đích chính. Với câu trả lời AI mang nội dung chuyên môn, bác sĩ/người có thẩm quyền phải xem xét; AI không tự chẩn đoán hoặc quyết định điều trị.
