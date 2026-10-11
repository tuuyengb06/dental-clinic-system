# User Story hệ thống quản lý nha khoa

## US-01 — Tiếp nhận bệnh nhân

**User story:** Là một lễ tân, tôi muốn tra cứu thông tin cần thiết của bệnh nhân theo quyền hạn để tiếp nhận và hỗ trợ đặt lịch.

**Tiêu chí chấp nhận:**
- Người dùng không có quyền không xem được hồ sơ bệnh nhân.
- Kết quả tra cứu chỉ hiển thị trường được phép theo vai trò.
- Không yêu cầu hoặc ghi dữ liệu bệnh nhân thật trong tiêu chí kiểm thử.

## US-02 — Tạo lịch hẹn

**User story:** Là một lễ tân, tôi muốn tạo lịch hẹn để điều phối thời gian khám cho bệnh nhân.

**Tiêu chí chấp nhận:**
- Lịch hẹn lưu thông tin cần thiết gồm bệnh nhân, thời gian, nhu cầu/dịch vụ, nhân viên phụ trách và trạng thái.
- Dữ liệu đầu vào được kiểm tra trước khi lưu.
- Quy tắc tránh trùng lịch và các trạng thái hợp lệ cần được xác nhận trước khi kiểm thử.

## US-03 — Cập nhật trạng thái lịch hẹn

**User story:** Là một lễ tân, tôi muốn cập nhật trạng thái lịch hẹn khi bệnh nhân đến khám để nhân viên theo dõi luồng tiếp nhận.

**Tiêu chí chấp nhận:**
- Chỉ người dùng được cấp quyền mới cập nhật được lịch.
- Trạng thái được lưu và hiển thị nhất quán.
- Danh sách trạng thái và chuyển trạng thái hợp lệ cần được xác nhận.

## US-04 — Ghi nhận thông tin khám

**User story:** Là một bác sĩ nha khoa, tôi muốn ghi nhận thông tin khám để lưu lại nội dung chuyên môn phục vụ theo dõi điều trị.

**Tiêu chí chấp nhận:**
- Chỉ người có quyền phù hợp mới xem hoặc cập nhật hồ sơ khám.
- Hệ thống lưu được ghi nhận gắn với hồ sơ phù hợp.
- Không hiển thị ghi chú chuyên môn cho actor không được cấp quyền.

## US-05 — Lập kế hoạch điều trị

**User story:** Là một bác sĩ nha khoa, tôi muốn lập kế hoạch điều trị để ghi lại định hướng chăm sóc do mình quyết định.

**Tiêu chí chấp nhận:**
- Kế hoạch được lưu gắn với hồ sơ liên quan và chỉ người được phân quyền mới truy cập.
- AI không tự lập hoặc xác nhận quyết định điều trị thay bác sĩ.
- Trường dữ liệu và quy trình chỉnh sửa cần được xác nhận.

## US-06 — Quản lý tài khoản và vai trò

**User story:** Là một quản trị viên, tôi muốn quản lý tài khoản nhân viên và vai trò để kiểm soát quyền truy cập hệ thống.

**Tiêu chí chấp nhận:**
- Chỉ quản trị viên được cấp quyền mới thay đổi vai trò.
- Quyền mới được áp dụng nhất quán theo chính sách hệ thống.
- Không hiển thị mật khẩu hoặc bí mật trong giao diện/log kiểm thử.

## US-07 — Xem báo cáo hoạt động

**User story:** Là một chủ phòng khám, tôi muốn xem báo cáo hoạt động theo tiêu chí hệ thống cung cấp để theo dõi vận hành.

**Tiêu chí chấp nhận:**
- Báo cáo chỉ bao gồm chỉ số đã được cấu hình.
- Quyền truy cập báo cáo được kiểm tra ở phía máy chủ.
- Không xuất thông tin bệnh nhân không cần thiết.

## US-08 — Xem báo cáo doanh thu

**User story:** Là một chủ phòng khám, tôi muốn xem doanh thu theo tiêu chí hệ thống cung cấp để theo dõi tình hình tài chính.

**Tiêu chí chấp nhận:**
- Kết quả tuân theo định nghĩa doanh thu và bộ lọc đã được xác nhận.
- Chỉ người được cấp quyền xem báo cáo.
- Báo cáo tổng hợp không chứa thông tin định danh bệnh nhân.

## US-09 — Hỏi đáp FAQ qua chatbot

**User story:** Là một khách hàng, tôi muốn hỏi chatbot về dịch vụ và lịch hẹn để tìm thông tin cơ bản thuận tiện.

**Tiêu chí chấp nhận:**
- Chatbot chỉ trả lời dựa trên nội dung đã được phòng khám phê duyệt.
- Khi thiếu dữ liệu, chatbot nói rõ và không tự đoán.
- Chatbot không chẩn đoán hoặc quyết định điều trị.

## US-10 — Rà soát nội dung AI hỗ trợ

**User story:** Là một bác sĩ nha khoa, tôi muốn xem và chỉnh sửa bản tóm tắt do AI hỗ trợ để tiết kiệm thời gian nhưng vẫn kiểm soát nội dung chuyên môn.

**Tiêu chí chấp nhận:**
- Bản AI không được tự lưu/sử dụng như kết luận chuyên môn khi chưa được bác sĩ xem xét.
- Bác sĩ có thể sửa hoặc từ chối nội dung trước khi sử dụng.
- Khi dữ liệu thiếu, AI nêu giới hạn thay vì tự bịa/chẩn đoán.

**Giả định cần xác nhận:** actor khách hàng có truy cập trực tiếp chatbot hay không; phân quyền chi tiết, quy tắc lịch hẹn và trường dữ liệu bắt buộc.
