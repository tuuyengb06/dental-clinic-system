# User Story theo mẫu Few-Shot

## Chức năng: Đặt lịch hẹn khám nha khoa

**User story:** Là một lễ tân, tôi muốn tạo lịch hẹn cho bệnh nhân để điều phối thời gian khám.

**Tiêu chí chấp nhận:**
- Khi nhập đủ thông tin lịch hẹn hợp lệ, hệ thống lưu bệnh nhân, thời gian, nhu cầu/dịch vụ, nhân viên phụ trách và trạng thái.
- Người không có quyền không thể xem hoặc sửa thông tin bệnh nhân gắn với lịch.
- Quy tắc tránh trùng lịch và danh sách trạng thái phải được xác nhận trước khi áp dụng.

## Chức năng: Ghi nhận kết quả khám và kế hoạch điều trị

**User story:** Là một bác sĩ nha khoa, tôi muốn ghi nhận thông tin khám và kế hoạch điều trị để theo dõi quá trình chăm sóc bệnh nhân.

**Tiêu chí chấp nhận:**
- Người có quyền phù hợp mới xem hoặc sửa hồ sơ khám.
- Nội dung lưu gắn với hồ sơ phù hợp và không hiển thị cho vai trò không được cấp quyền.
- AI không tự tạo chẩn đoán/quyết định điều trị; nội dung AI hỗ trợ phải được bác sĩ xem xét, xác nhận.

## Chức năng: Lập hóa đơn và ghi nhận thanh toán

**User story:** Là một nhân viên được phân quyền, tôi muốn lập hóa đơn cho dịch vụ đã được xác nhận và ghi nhận thanh toán để lưu giao dịch của phòng khám.

**Tiêu chí chấp nhận:**
- Tổng tiền được tính từ dịch vụ/số lượng/đơn giá theo quy tắc đã cấu hình.
- Chỉ nhân viên có quyền lập hoặc ghi nhận thanh toán mới thực hiện được thao tác.
- Không tự suy ra quy tắc giảm giá, hủy hoặc hoàn tiền chưa được xác nhận.

## Chức năng: Xem báo cáo doanh thu theo ngày/tháng

**User story:** Là một chủ phòng khám, tôi muốn xem doanh thu theo ngày hoặc tháng để theo dõi hoạt động tài chính.

**Tiêu chí chấp nhận:**
- Chỉ tiêu và trạng thái giao dịch được tính theo định nghĩa doanh thu đã được xác nhận.
- Kết quả được tổng hợp theo kỳ đã chọn và không hiển thị thông tin định danh bệnh nhân.
- Người không có quyền báo cáo không thể truy cập endpoint/dữ liệu.

## Chức năng: Hỏi đáp dữ liệu hoạt động bằng ngôn ngữ tự nhiên

**User story:** Là một chủ phòng khám được cấp quyền, tôi muốn hỏi dữ liệu hoạt động bằng ngôn ngữ tự nhiên để nhanh chóng theo dõi chỉ số cần thiết.

**Tiêu chí chấp nhận:**
- Câu trả lời chỉ dựa trên dữ liệu tổng hợp mà người hỏi được phép truy cập.
- Nếu truy vấn/dữ liệu không đủ, hệ thống nói rõ giới hạn và không bịa số liệu.
- Câu trả lời không tiết lộ hồ sơ sức khỏe hoặc định danh bệnh nhân.
