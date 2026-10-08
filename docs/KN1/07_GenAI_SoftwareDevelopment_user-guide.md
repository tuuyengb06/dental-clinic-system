# 1. GIỚI THIỆU TỔNG QUAN HỆ THỐNG

## 1.1. Mục tiêu tài liệu
Tài liệu này giúp người dùng cuối làm việc với hệ thống quản lý nha khoa một cách dễ dàng, an toàn và đúng quyền hạn. Mỗi vai trò sẽ có những thao tác phù hợp với chức năng của mình, giúp tiết kiệm thời gian và tránh sai sót trong quá trình làm việc.

## 1.2. Người dùng chính
- ACT-001: Quản trị viên — quản lý người dùng, quyền truy cập và báo cáo tổng quan.
- ACT-002: Bác sĩ — quản lý hồ sơ bệnh nhân, ghi nhận điều trị và theo dõi tái khám.
- ACT-003: Lễ tân — quản lý lịch hẹn, bệnh nhân và hóa đơn ban đầu.
- ACT-004: Hệ thống AI — hỗ trợ tóm tắt, nhắc tái khám và giải thích dịch vụ theo hướng dẫn y tế.

## 1.3. Các màn hình chính
- Màn hình đăng nhập
- Màn hình quản lý bệnh nhân
- Màn hình lịch hẹn
- Màn hình hồ sơ điều trị
- Màn hình thanh toán
- Màn hình nhắc tái khám
- Màn hình hỗ trợ AI

## 1.4. Nguyên tắc sử dụng
- Mỗi người dùng chỉ thực hiện chức năng theo vai trò được cấp.
- Trước khi lưu thông tin, hãy kiểm tra dữ liệu đầu vào rõ ràng và đầy đủ.
- Nếu hệ thống báo lỗi, đọc thông báo, sửa thông tin rồi thử lại.
- Mọi kết quả từ AI chỉ mang tính hỗ trợ; bác sĩ vẫn là người quyết định cuối cùng.

# 2. BẢNG PHÂN QUYỀN SỬ DỤNG THEO VAI TRÒ

| Vai trò | Mã vai trò | Chức năng được phép | Mô tả ngắn |
|---|---|---|---|
| Quản trị viên | ACT-001 | UC-001, UC-006 | Quản lý tài khoản, quyền truy cập, theo dõi tình trạng vận hành |
| Bác sĩ | ACT-002 | UC-002, UC-004, UC-005 | Xem hồ sơ bệnh nhân, cập nhật điều trị, xem hỗ trợ AI |
| Lễ tân | ACT-003 | UC-002, UC-003, UC-006 | Quản lý bệnh nhân, lịch hẹn và thanh toán ban đầu |
| Hệ thống AI | ACT-004 | UC-005 | Hỗ trợ tóm tắt, nhắc tái khám, giải thích dịch vụ |

# 3. HƯỚNG DẪN THAO TÁC CHI TIẾT (STEP-BY-STEP GUIDES)

## 3.1. UG-001: Đăng nhập hệ thống
- Mã hướng dẫn: `UG-001`
- Tên chức năng: Đăng nhập
- Use Case liên kết: `UC-001`
- Yêu cầu quyền: Tất cả người dùng có tài khoản

### Bước thực hiện
1. Mở màn hình đăng nhập.
2. Nhập tên đăng nhập và mật khẩu.
3. Chọn nút Đăng nhập.
4. Nếu thông tin đúng, hệ thống sẽ chuyển đến màn hình chính theo vai trò của bạn.
5. Nếu sai, hệ thống sẽ hiển thị thông báo lỗi và yêu cầu nhập lại.

### Dữ liệu cần nhập
- Tên đăng nhập
- Mật khẩu

### Thông báo trả về
- Đăng nhập thành công: chuyển hướng đến giao diện phù hợp.
- Đăng nhập thất bại: hiển thị cảnh báo sai thông tin.
- Tài khoản khóa: hiển thị thông báo liên hệ quản trị viên.

### Giao diện mẫu
- Trường tên đăng nhập
- Trường mật khẩu
- Nút Đăng nhập
- Nút Quên mật khẩu (nếu có)

---

## 3.2. UG-002: Quản lý hồ sơ bệnh nhân
- Mã hướng dẫn: `UG-002`
- Tên chức năng: Tạo và cập nhật hồ sơ bệnh nhân
- Use Case liên kết: `UC-002`
- Yêu cầu quyền: Lễ tân, bác sĩ, quản trị viên

### Bước thực hiện
1. Chọn mục Quản lý bệnh nhân từ menu chính.
2. Chọn nút Thêm bệnh nhân mới hoặc mở hồ sơ hiện có.
3. Điền thông tin bắt buộc: họ tên, số điện thoại, tiền sử bệnh lý, dị ứng nếu có.
4. Kiểm tra lại dữ liệu trước khi lưu.
5. Chọn nút Lưu để hoàn tất.

### Dữ liệu cần nhập
- Họ tên bệnh nhân
- Số điện thoại
- Email (nếu có)
- Ngày sinh
- Tiền sử bệnh lý
- Dị ứng

### Thông báo trả về
- Hồ sơ mới được lưu thành công.
- Nếu thiếu dữ liệu bắt buộc, hệ thống báo lỗi và yêu cầu nhập lại.
- Nếu bệnh nhân đã tồn tại, hệ thống cảnh báo kiểm tra trùng lặp.

### Giao diện mẫu
- Bảng danh sách bệnh nhân
- Form thông tin cá nhân
- Nút Lưu, Sửa, Xóa (theo quyền)

---

## 3.3. UG-003: Đặt lịch hẹn
- Mã hướng dẫn: `UG-003`
- Tên chức năng: Đặt lịch khám
- Use Case liên kết: `UC-003`
- Yêu cầu quyền: Lễ tân, quản trị viên

### Bước thực hiện
1. Chọn mục Lịch hẹn trên màn hình chính.
2. Chọn bệnh nhân cần đặt lịch.
3. Chọn bác sĩ và thời gian khám.
4. Ghi chú nếu có nhu cầu đặc biệt.
5. Chọn nút Xác nhận lịch hẹn.
6. Hệ thống sẽ kiểm tra xem khung giờ đó có trùng với lịch của bác sĩ hay không.

### Dữ liệu cần nhập
- Tên bệnh nhân
- Bác sĩ khám
- Thời gian khám
- Ghi chú bổ sung

### Thông báo trả về
- Lịch hẹn được lưu thành công.
- Nếu bác sĩ đã có lịch cùng thời gian, hệ thống báo xung đột và không lưu.
- Nếu thiếu dữ liệu cần thiết, hệ thống yêu cầu nhập lại.

### Giao diện mẫu
- Danh sách lịch trong ngày
- Form đặt lịch
- Cột trạng thái: chờ xác nhận, đã xác nhận, đã hủy

---

## 3.4. UG-004: Cập nhật hồ sơ điều trị
- Mã hướng dẫn: `UG-004`
- Tên chức năng: Ghi nhận điều trị
- Use Case liên kết: `UC-004`
- Yêu cầu quyền: Bác sĩ

### Bước thực hiện
1. Mở hồ sơ bệnh nhân cần điều trị.
2. Chọn tab Hồ sơ điều trị.
3. Nhập chẩn đoán, y lệnh và thủ thuật đã thực hiện.
4. Chọn trạng thái điều trị: đang xử lý, đã xong hoặc chờ theo dõi.
5. Chọn nút Lưu hồ sơ.

### Dữ liệu cần nhập
- Chẩn đoán
- Y lệnh
- Thủ thuật hoặc quy trình thực hiện
- Trạng thái tiến độ điều trị

### Thông báo trả về
- Hồ sơ điều trị được cập nhật thành công.
- Nếu thiếu thông tin bắt buộc, hệ thống cảnh báo và từ chối lưu.
- Nếu điều trị chưa hoàn tất, hệ thống nhắc nhở cần tiếp tục theo dõi.

### Giao diện mẫu
- Thẻ thông tin bệnh nhân
- Form chẩn đoán và điều trị
- Nút Lưu, In hồ sơ, Xem tiến độ

---

## 3.5. UG-005: Tạo hóa đơn và thanh toán
- Mã hướng dẫn: `UG-005`
- Tên chức năng: Lập hóa đơn và ghi nhận thanh toán
- Use Case liên kết: `UC-006`
- Yêu cầu quyền: Lễ tân, quản trị viên

### Bước thực hiện
1. Chọn bệnh nhân có lịch khám hoặc dịch vụ được thực hiện.
2. Chọn các dịch vụ cần thanh toán.
3. Hệ thống tự tính tổng tiền.
4. Chọn phương thức thanh toán phù hợp.
5. Xác nhận thanh toán hoặc lưu ở trạng thái chờ thanh toán.
6. Chọn nút Lập hóa đơn.

### Dữ liệu cần nhập
- Dịch vụ sử dụng
- Số lượng
- Phương thức thanh toán
- Trạng thái thanh toán

### Thông báo trả về
- Hóa đơn được lưu thành công.
- Nếu thiếu thông tin thanh toán, hệ thống cảnh báo.
- Nếu thanh toán chưa hoàn tất, hóa đơn vẫn giữ trạng thái chờ thanh toán.

### Giao diện mẫu
- Bảng danh sách dịch vụ
- Cột tổng tiền
- Nút Tạo hóa đơn
- Trạng thái thanh toán

---

## 3.6. UG-006: Tạo nhắc tái khám
- Mã hướng dẫn: `UG-006`
- Tên chức năng: Gửi nhắc tái khám
- Use Case liên kết: `UC-005`
- Yêu cầu quyền: Bác sĩ, quản trị viên

### Bước thực hiện
1. Mở hồ sơ bệnh nhân hoặc lịch khám gần nhất.
2. Xác định ngày tái khám phù hợp.
3. Kiểm tra thông tin bệnh nhân và lịch sử điều trị.
4. Tạo lời nhắc tái khám.
5. Gửi hoặc lưu nhắc nếu cần.

### Dữ liệu cần nhập
- Ngày tái khám
- Thông tin bệnh nhân
- Lời nhắn nhắc nhở
- Cảnh báo y tế nếu cần

### Thông báo trả về
- Nhắc tái khám được tạo thành công.
- Nếu ngày tái khám không hợp lệ, hệ thống báo lỗi.
- Nếu có cảnh báo y tế, nhắn nhắc được thêm nội dung an toàn.

### Giao diện mẫu
- Mục Tái khám
- Nút Tạo nhắc
- Danh sách nhắc nhở đã gửi

---

## 3.7. UG-007: Sử dụng hỗ trợ AI
- Mã hướng dẫn: `UG-007`
- Tên chức năng: Tóm tắt điều trị và giải thích dịch vụ
- Use Case liên kết: `UC-005`
- Yêu cầu quyền: Bác sĩ, quản trị viên

### Bước thực hiện
1. Chọn chức năng AI từ menu.
2. Chọn loại hỗ trợ: tóm tắt điều trị, giải thích dịch vụ hoặc nhắc tái khám.
3. Nhập hoặc chọn dữ liệu cần xử lý.
4. Chọn nút Gửi yêu cầu.
5. Kiểm tra kết quả AI trước khi lưu hoặc chia sẻ.
6. Nếu có cảnh báo y tế, đọc kỹ và xác nhận lại với bác sĩ trước khi đưa vào hồ sơ.

### Dữ liệu cần nhập
- Ghi chú lâm sàng
- Thông tin dịch vụ
- Ngày tái khám
- Mô tả cần giải thích

### Thông báo trả về
- AI trả về kết quả tóm tắt hoặc lời giải thích.
- Nếu AI quá thời gian hoặc phản hồi không hợp lệ, hệ thống báo lỗi và yêu cầu thử lại.
- Nếu có cảnh báo y tế, hệ thống yêu cầu người dùng xem xét kỹ lưỡng.

### Giao diện mẫu
- Trình chọn chức năng AI
- Khung dữ liệu đầu vào
- Nút Gửi yêu cầu
- Khu vực hiển thị kết quả
- Nút Lưu hoặc Bỏ qua

# 4. DANH MỤC THÔNG BÁO VÀ HƯỚNG DẪN XỬ LÝ LỖI (FAQ)

## 4.1. Lỗi thường gặp và cách xử lý
| Mã lỗi | Cảnh báo người dùng | Nguyên nhân thường gặp | Cách xử lý |
|---|---|---|---|
| ERR-001 | Tên đăng nhập hoặc mật khẩu sai | Sai thông tin tài khoản | Kiểm tra lại tên đăng nhập và mật khẩu |
| ERR-002 | Hồ sơ bệnh nhân chưa đầy đủ | Thiếu thông tin bắt buộc | Điền đủ thông tin rồi lưu lại |
| ERR-003 | Khung giờ đã được đặt | Bác sĩ đã có lịch cùng thời điểm | Chọn khung giờ khác |
| ERR-004 | Hồ sơ điều trị chưa hoàn tất | Chưa nhập chẩn đoán hoặc y lệnh | Hoàn thiện thông tin điều trị trước khi lưu |
| ERR-005 | Hóa đơn chưa có phương thức thanh toán | Thiếu thông tin thanh toán | Chọn phương thức thanh toán hợp lệ |
| ERR-006 | Không thể tạo nhắc tái khám | Ngày tái khám không hợp lệ | Kiểm tra lại ngày và nhập đúng định dạng |
| ERR-007 | Kết quả AI không rõ ràng | Dữ liệu đầu vào thiếu hoặc mô hình chưa phản hồi | Kiểm tra dữ liệu đầu vào và thử lại |
| ERR-008 | Có cảnh báo y tế | Dữ liệu có nguy cơ ảnh hưởng đến an toàn | Xem lại với bác sĩ trước khi xác nhận |

## 4.2. Khuyến nghị thực hành
- Không nhập khẩu nguyên liệu nhạy cảm không cần thiết vào AI.
- Luôn kiểm tra thông tin bệnh nhân trước khi lưu lịch hẹn hoặc thanh toán.
- Khi kết quả AI chưa rõ, hãy hỏi thêm thông tin hoặc nhờ bác sĩ xác nhận.
- Nên cập nhật hồ sơ điều trị ngay sau mỗi buổi khám để tránh sai lệch bị trễ.

# 5. MA TRẬN TRUY VẾT HƯỚNG DẪN SỬ DỤNG (STAGE 4)

| Mã hướng dẫn | Tên hướng dẫn | Use Case liên quan | Vai trò chính |
|---|---|---|---|
| UG-001 | Đăng nhập hệ thống | UC-001 | ACT-001, ACT-002, ACT-003 |
| UG-002 | Quản lý hồ sơ bệnh nhân | UC-002 | ACT-001, ACT-002, ACT-003 |
| UG-003 | Đặt lịch hẹn | UC-003 | ACT-001, ACT-003 |
| UG-004 | Cập nhật hồ sơ điều trị | UC-004 | ACT-002 |
| UG-005 | Tạo hóa đơn và thanh toán | UC-006 | ACT-001, ACT-003 |
| UG-006 | Tạo nhắc tái khám | UC-005 | ACT-002 |
| UG-007 | Sử dụng hỗ trợ AI | UC-005 | ACT-002, ACT-004 |

## 5.1. Kết luận
Tài liệu hướng dẫn sử dụng này được xây dựng theo logic người dùng cuối: rõ ràng, dễ làm theo, gắn với vai trò và chức năng cụ thể. Người dùng có thể thao tác chính xác các bước từ đăng nhập, quản lý bệnh nhân, đặt lịch, cập nhật điều trị, lập hóa đơn đến sử dụng hỗ trợ AI. Mỗi hướng dẫn đều có mối liên kết trực tiếp với use case tương ứng, đảm bảo tính nhất quán với các tài liệu phân tích và thiết kế trước đó.
