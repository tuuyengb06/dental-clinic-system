# 1. CHIẾN LƯỢC VÀ PHẠM VI KIỂM THỬ

## 1.1. Mục tiêu kiểm thử
Kiểm thử chức năng nhằm xác nhận hệ thống quản lý nha khoa có tích hợp AI hoạt động đúng theo yêu cầu đã được định nghĩa trong SRS, bao gồm: đăng nhập và phân quyền, quản lý bệnh nhân, lịch hẹn, hồ sơ điều trị, dịch vụ, thanh toán và AI hỗ trợ. Mục tiêu là đảm bảo tính đúng đắn, độ ổn định và khả năng xử lý ngoại lệ trong môi trường demo local.

## 1.2. Phạm vi kiểm thử
- Kiểm thử Black-box cho toàn bộ chức năng nghiệp vụ.
- Kiểm thử Unit và Integration ở mức logic nghiệp vụ với dữ liệu demo.
- Kiểm thử Boundary và Exception Flow cho các trường hợp dữ liệu không hợp lệ, xung đột lịch, timeout AI và phân quyền gắn với vai trò.

## 1.3. Các mức kiểm thử áp dụng
- Unit Testing: validate logic xác thực, tính toán tiền, kiểm tra xung đột lịch, ràng buộc dữ liệu đầu vào.
- Integration Testing: kiểm tra tương tác giữa service, repository và AI module.
- System Testing: kiểm tra luồng người dùng hoàn chỉnh từ đăng nhập đến thanh toán và nhận kết quả AI.

## 1.4. Tiêu chí chấp nhận
- 100% REQ-F và BR phải có ít nhất 1 Positive Test Case và 1 Negative Test Case.
- Mọi Test Case phải có mã TC-xxx, liên kết với UC hoặc REQ tương ứng.
- Không nhúng cấu trúc SQL hoặc tên cột DB vào test case.

# 2. DANH SÁCH KỊCH BẢN KIỂM THỬ (TEST SCENARIOS)

| Mã kịch bản | Tên kịch bản | Liên kết |
|---|---|---|
| TS-001 | Đăng nhập với tài khoản hợp lệ | REQ-F-001, UC-001 |
| TS-002 | Đăng nhập với thông tin sai | REQ-F-001, UC-001, BR-001 |
| TS-003 | Tạo hồ sơ bệnh nhân hợp lệ | REQ-F-002, UC-002 |
| TS-004 | Tạo hồ sơ bệnh nhân không hợp lệ | REQ-F-002, UC-002, BR-003 |
| TS-005 | Đặt lịch khám không xung đột | REQ-F-003, UC-003 |
| TS-006 | Đặt lịch khám trùng khung giờ | REQ-F-003, UC-003, BR-002 |
| TS-007 | Cập nhật hồ sơ điều trị | REQ-F-004, UC-004 |
| TS-008 | Cập nhật hồ sơ điều trị thiếu dữ liệu | REQ-F-004, UC-004, BR-004 |
| TS-009 | Tạo hóa đơn và cập nhật thanh toán | REQ-F-005, UC-006 |
| TS-010 | Tạo nhắc tái khám từ dữ liệu hợp lệ | REQ-F-006, UC-005 |
| TS-011 | AI tóm tắt điều trị | REQ-F-007, UC-005 |
| TS-012 | AI giải thích dịch vụ có cảnh báo | REQ-F-007, UC-005, BR-007 |
| TS-013 | AI timeout hoặc phản hồi không hợp lệ | REQ-F-007, UC-005, BR-008 |

# 3. MA TRẬN BAO PHỦ KIỂM THỬ (TEST COVERAGE MATRIX)

| Mã REQ / BR | Positive Test Case | Negative Test Case | Ghi chú |
|---|---|---|---|
| REQ-F-001 | TC-001 | TC-002 | Đăng nhập và phân quyền |
| REQ-F-002 | TC-003 | TC-004 | Hồ sơ bệnh nhân |
| REQ-F-003 | TC-005 | TC-006 | Lịch hẹn và xung đột |
| REQ-F-004 | TC-007 | TC-008 | Hồ sơ điều trị |
| REQ-F-005 | TC-009 | TC-010 | Hóa đơn và thanh toán |
| REQ-F-006 | TC-011 | TC-012 | Tái khám |
| REQ-F-007 | TC-013 | TC-014 | AI và cảnh báo |
| BR-001 | TC-001 | TC-002 | Phân quyền |
| BR-002 | TC-005 | TC-006 | Trùng lịch |
| BR-003 | TC-003 | TC-004 | Dữ liệu bệnh nhân |
| BR-004 | TC-007 | TC-008 | Cập nhật điều trị |
| BR-005 | TC-009 | TC-010 | Hóa đơn |
| BR-006 | TC-011 | TC-012 | Nhắc tái khám |
| BR-007 | TC-013 | TC-014 | Cảnh báo của AI |
| BR-008 | TC-013 | TC-014 | Bảo mật dữ liệu khi gọi AI |

# 4. BẢNG ĐẶC TẢ CHI TIẾT TEST CASES

| Mã TC | UC / REQ Liên kết | Tên Test Case | Điều kiện tiền đề | Các bước thực hiện | Dữ liệu mẫu (Logic) | Kết quả kỳ vọng | Ưu tiên |
|---|---|---|---|---|---|---|---|
| TC-001 | UC-001 / REQ-F-001 | Đăng nhập thành công | Người dùng đã có tài khoản hợp lệ | 1. Mở màn hình đăng nhập. 2. Nhập username hợp lệ. 3. Nhập mật khẩu đúng. 4. Chọn đăng nhập. | Username hợp lệ, mật khẩu đúng, vai trò đã được phân quyền | Hệ thống đăng nhập thành công và chuyển đến màn hình phù hợp với vai trò | High |
| TC-002 | UC-001 / REQ-F-001 / BR-001 | Đăng nhập sai thông tin | Người dùng chưa được xác thực | 1. Mở màn hình đăng nhập. 2. Nhập username đúng nhưng mật khẩu sai. 3. Chọn đăng nhập. | Username đúng, mật khẩu sai | Hệ thống hiển thị lỗi xác thực và không cho truy cập | High |
| TC-003 | UC-002 / REQ-F-002 / BR-003 | Tạo hồ sơ bệnh nhân hợp lệ | Người dùng đã đăng nhập với quyền cho phép | 1. Mở trang quản lý bệnh nhân. 2. Nhập thông tin cá nhân rõ ràng. 3. Lưu hồ sơ. | Họ tên đầy đủ, số điện thoại đúng định dạng, tiền sử bệnh lý mô tả rõ ràng | Hồ sơ bệnh nhân được lưu thành công | High |
| TC-004 | UC-002 / REQ-F-002 / BR-003 | Tạo hồ sơ bệnh nhân thiếu dữ liệu bắt buộc | Người dùng đã đăng nhập | 1. Mở quản lý bệnh nhân. 2. Bỏ trống họ tên hoặc thông tin bắt buộc. 3. Lưu. | Họ tên trống hoặc số điện thoại không hợp lệ | Hệ thống báo lỗi và không lưu hồ sơ | High |
| TC-005 | UC-003 / REQ-F-003 / BR-002 | Đặt lịch hẹn không có xung đột | Bệnh nhân đã có hồ sơ tồn tại | 1. Mở màn hình lịch hẹn. 2. Chọn bác sĩ và thời gian rảnh. 3. Lưu lịch hẹn. | Bác sĩ phù hợp, khoảng thời gian chưa được đặt | Hệ thống lưu lịch hẹn thành công | High |
| TC-006 | UC-003 / REQ-F-003 / BR-002 | Đặt lịch hẹn trùng khung giờ | Bác sĩ đã có lịch hẹn trong khung giờ đó | 1. Chọn cùng bác sĩ và cùng thời gian đã có lịch. 2. Lưu. | Khung giờ bị trùng với lịch hẹn đã tồn tại | Hệ thống hiển thị cảnh báo xung đột và không lưu | High |
| TC-007 | UC-004 / REQ-F-004 / BR-004 | Cập nhật hồ sơ điều trị hợp lệ | Bệnh nhân đã có lịch hẹn và bác sĩ đã đăng nhập | 1. Mở hồ sơ bệnh nhân. 2. Nhập chẩn đoán, y lệnh và thủ thuật. 3. Lưu hồ sơ. | Chẩn đoán rõ ràng, y lệnh đầy đủ | Hồ sơ điều trị được lưu và cập nhật đúng | High |
| TC-008 | UC-004 / REQ-F-004 / BR-004 | Cập nhật hồ sơ điều trị thiếu thông tin | Bác sĩ đã đăng nhập | 1. Mở hồ sơ bệnh nhân. 2. Chỉ nhập chẩn đoán nhưng thiếu y lệnh hoặc thủ thuật. 3. Lưu. | Dữ liệu thiếu trường bắt buộc | Hệ thống báo lỗi và không chốt hồ sơ | High |
| TC-009 | UC-006 / REQ-F-005 / BR-005 | Tạo hóa đơn và xác nhận thanh toán | Dịch vụ và lịch hẹn đã xác nhận | 1. Mở quản lý thanh toán. 2. Chọn dịch vụ và phương thức thanh toán. 3. Lưu hóa đơn. | Tổng tiền hợp lệ, phương thức thanh toán hợp lệ | Hệ thống lưu hóa đơn và trạng thái thanh toán đúng | High |
| TC-010 | UC-006 / REQ-F-005 / BR-005 | Tạo hóa đơn thiếu thông tin thanh toán | Dịch vụ đã được chọn | 1. Mở hóa đơn. 2. Không nhập phương thức thanh toán hoặc tổng tiền. 3. Lưu. | Phương thức thanh toán trống hoặc tổng tiền không hợp lệ | Hệ thống báo lỗi và không lưu hóa đơn | Medium |
| TC-011 | UC-005 / REQ-F-006 / BR-006 | Tạo nhắc tái khám từ dữ liệu hợp lệ | Có bệnh nhân đã có lịch tái khám được ghi nhận | 1. Mở chức năng theo dõi tái khám. 2. Xác nhận ngày tái khám. 3. Tạo nhắc nhở. | Ngày tái khám hợp lệ, bệnh nhân đã có hồ sơ | Hệ thống sinh tin nhắn nhắc tái khám hợp lệ | High |
| TC-012 | UC-005 / REQ-F-006 / BR-006 | Tạo nhắc tái khám với dữ liệu không hợp lệ | Hệ thống có dữ liệu bệnh nhân nhưng thiếu ngày tái khám | 1. Chọn bệnh nhân. 2. Bỏ trống ngày tái khám. 3. Tạo nhắc. | Ngày tái khám bị thiếu hoặc sai định dạng | Hệ thống báo lỗi và không tạo nhắc nhở | Medium |
| TC-013 | UC-005 / REQ-F-007 / BR-007 | AI giải thích dịch vụ có cảnh báo y tế | Bác sĩ hoặc người dùng đưa vào dữ liệu dịch vụ hợp lệ | 1. Chọn chức năng giải thích dịch vụ. 2. Gửi thông tin dịch vụ. 3. Gửi yêu cầu giải thích. | Tên dịch vụ rõ ràng, mô tả dịch vụ phù hợp | Hệ thống trả về giải thích bằng ngôn ngữ dễ hiểu đồng thời có cảnh báo y tế rõ ràng | High |
| TC-014 | UC-005 / REQ-F-007 / BR-008 | AI timeout hoặc trả về dữ liệu không hợp lệ | AI module đang chạy hoặc có lỗi kết nối | 1. Gửi yêu cầu AI. 2. Ngắt kết nối mô hình hoặc tạo phản hồi thiếu định dạng. | Yêu cầu AI không đủ dữ liệu hoặc timeout | Hệ thống hiển thị cảnh báo lỗi, yêu cầu thử lại hoặc bỏ qua kết quả không hợp lệ | High |

## 4.1. Kết luận kiểm thử
Các test case trên bao phủ hầu hết các chức năng cốt lõi và các luồng ngoại lệ quan trọng của hệ thống quản lý nha khoa có tích hợp AI. Mỗi yêu cầu chức năng và quy tắc nghiệp vụ đều có ít nhất một positive và negative test case phù hợp với mô tả của SRS. Lưu ý quan trọng là các test data ở đây chỉ ở mức logic nghiệp vụ, không phụ thuộc vào cấu trúc bảng CSDL vật lý hay tên cột SQL.
