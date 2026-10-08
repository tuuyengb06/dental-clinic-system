## 1. TỔNG QUAN HỆ THỐNG QUẢN LÝ NHA KHOA TÍCH HỢP AI

### 1.1. Mục đích và Phạm vi

Hệ thống phần mềm quản lý phòng khám nha khoa tích hợp Trí tuệ Nhân tạo (AI) được xây dựng nhằm tự động hóa quy trình nghiệp vụ cốt lõi, tối ưu hóa công tác điều trị của đội ngũ bác sĩ, nâng cao chất lượng phục vụ bệnh nhân và hỗ trợ ban quản lý ra quyết định tài chính.

* **Phạm vi trong hệ thống (In-Scope)**: Quản lý hồ sơ bệnh nhân, lịch sử khám răng; Quản lý lịch làm việc và phân ca của bác sĩ; Đặt lịch hẹn và chống trùng lịch trực; Quản lý hồ sơ điều trị lâm sàng; Danh mục dịch vụ nha khoa; Quản lý thanh toán, hóa đơn và công nợ; Lịch tái khám tự động; Tích hợp 3 tính năng AI (Tóm tắt ghi chú điều trị, Sinh tin nhắn nhắc lịch tái khám, Giải thích dịch vụ y tế phổ thông).
* **Phạm vi ngoài hệ thống (Out-of-Scope)**: Tích hợp thiết bị phần cứng chụp X-quang/CT trực tiếp vào phần mềm; Hệ thống BHYT nhà nước; Thanh toán cổng thanh toán quốc tế phức tạp ngoài các phương thức cơ bản.

### 1.2. Các bên liên quan (Stakeholders) và Phân quyền

* **Quản trị viên (Admin)**: Quản lý toàn bộ hệ thống, phân quyền người dùng, cấu hình tham số hệ thống và quản lý tài khoản nhân viên.
* **Bác sĩ (Doctor)**: Đọc lịch hẹn, tiếp nhận bệnh nhân, ghi chú lâm sàng, lập y lệnh điều trị, chỉ định dịch vụ, sử dụng AI tóm tắt hồ sơ điều trị.
* **Lễ tân / Nhân viên (Receptionist)**: Tiếp đón bệnh nhân, tạo hồ sơ bệnh nhân mới, đăng ký và xếp lịch hẹn, lập hóa đơn thanh toán.
* **Bệnh nhân (Patient/User)**: Tra cứu lịch sử khám chữa bệnh cá nhân, nhận tin nhắn nhắc lịch tái khám và đọc thông tin giải thích dịch vụ do AI hỗ trợ.

---

## 2. QUY TRÌNH PHÁT TRIỂN PHẦN MỀM (SDLC) VÀ ỨNG DỤNG AI

Quy trình phát triển phần mềm được chia thành 4 giai đoạn chuẩn hóa theo mô hình SDLC tích hợp công nghệ AI trợ giúp:

### Giai đoạn 1: Phân tích yêu cầu và thiết kế hệ thống (Bài KT1)

* Sử dụng AI phân tích quy trình nghiệp vụ tiếp đón bệnh nhân, khám răng và lập hóa đơn tại phòng khám nha khoa.
* AI hỗ trợ định hình danh sách tác nhân (Actors), Use Cases, Yêu cầu phi chức năng và sơ đồ thực thể mối quan hệ (ERD).
* Xác định chính xác các điểm chạm tích hợp AI trong hệ thống quản lý.

### Giai đoạn 2: Xây dựng chức năng quản lý (Bài KT2)

* Sử dụng AI hỗ trợ sinh mã nguồn khung (boilerplate), cấu trúc thư mục, mô hình dữ liệu (Models/Schemas) và các API CRUD cơ bản.
* Xây dựng câu lệnh truy vấn xử lý tính toán doanh thu, tồn kho vật tư và thuật toán kiểm tra trùng lịch hẹn của bác sĩ.
* Lưu trữ nhật ký prompt làm minh chứng học tập và phát triển.

### Giai đoạn 3: Tích hợp AI, tối ưu prompt và kiểm thử (Bài KT3)

* Thiết kế, kiểm thử và tối ưu hóa các mẫu Prompt chuyên biệt cho tính năng tóm tắt điều trị và nhắc lịch tái khám.
* Xây dựng cơ chế xử lý lỗi khi gọi API AI (timeout, giới hạn tần suất, định dạng phản hồi sai cấu trúc).
* Lập bộ kịch bản kiểm thử (Test Cases) toàn diện cho cả chức năng quản lý lẫn tính năng AI.

### Giai đoạn 4: Hoàn thiện, triển khai và báo cáo (Bài thi cuối kỳ)

* Soạn thảo tài liệu hướng dẫn cài đặt (`README.md`), thiết lập biến môi trường (`.env.example`) và kịch bản dữ liệu mẫu.
* Rà soát mã nguồn (code review) bằng AI để phát hiện lỗ hổng bảo mật và phân quyền dữ liệu.
* Tổng hợp báo cáo kỹ thuật, chuẩn bị slide demo sản phẩm và hoàn thiện đồ án.

---

## 3. ĐẶC TẢ YÊU CẦU CHỨC NĂNG VÀ PHI CHỨC NĂNG

### 3.1. Danh mục Yêu cầu Chức năng (Functional Requirements)

* **REQ-F-001**: Hệ thống phải cho phép người dùng đăng nhập, đăng xuất và phân quyền truy cập theo 3 vai trò: Quản trị viên, Bác sĩ, Lễ tân.
* **REQ-F-002**: Lễ tân có thể thêm mới, cập nhật và tìm kiếm thông tin bệnh nhân (họ tên, số điện thoại, tiền sử dị ứng, lịch sử khám).
* **REQ-F-003**: Hệ thống hỗ trợ quản lý danh mục dịch vụ nha khoa (mã dịch vụ, tên dịch vụ, đơn giá, mô tả chuyên môn).
* **REQ-F-004**: Cho phép đặt lịch hẹn khám răng, tự động kiểm tra khung giờ trống của bác sĩ nhằm tránh xung đột thời gian.
* **REQ-F-005**: Bác sĩ có thể tạo và cập nhật hồ sơ điều trị răng miệng (ghi nhận chẩn đoán, y lệnh, thủ thuật thực hiện kèm ghi chú lâm sàng).
* **REQ-F-006**: Lập hóa đơn thanh toán dịch vụ, áp dụng giảm giá (nếu có), ghi nhận phương thức thanh toán và trạng thái hoàn tất.
* **REQ-F-007**: Tự động hoặc thủ công tạo lịch tái khám dựa trên chu kỳ điều trị của bác sĩ.
* **REQ-F-008 (AI-01)**: **Tóm tắt quá trình điều trị**: AI nhận đầu vào là các ghi chú lâm sàng dài và sinh ra bản tóm tắt tiến trình điều trị gọn gàng cho bác sĩ.
* **REQ-F-009 (AI-02)**: **Sinh tin nhắn nhắc lịch**: AI tự động tạo nội dung tin nhắn cá nhân hóa gửi nhắc lịch tái khám cho bệnh nhân.
* **REQ-F-010 (AI-03)**: **Giải thích dịch vụ y tế**: AI chuyển đổi thuật ngữ chuyên môn thành ngôn ngữ phổ thông để giải thích dịch vụ cho bệnh nhân kèm theo cảnh báo y tế bắt buộc.

### 3.2. Yêu cầu Phi chức năng (Non-Functional Requirements)

* **REQ-NF-001 (Bảo mật)**: Mật khẩu người dùng phải được mã hóa bằng thuật toán an toàn (như Bcrypt); dữ liệu cá nhân nhạy cảm của bệnh nhân phải được ẩn danh khi gọi API AI.
* **REQ-NF-002 (Hiệu năng)**: Thời gian phản hồi các truy vấn tra cứu thông tin bệnh nhân và danh mục dịch vụ dưới 2 giây.
* **REQ-NF-003 (Độ khả dụng)**: Hệ thống hoạt động ổn định trên môi trường local, hỗ trợ đồng thời nhiều phiên làm việc của nhân viên lễ tân và bác sĩ.

---

## 4. THIẾT KẾ CƠ SỞ DỮ LIỆU (DATABASE SCHEMA)

Cơ sở dữ liệu quan hệ được thiết kế tuân thủ chuẩn hóa 3NF, bảo đảm tính toàn vẹn dữ liệu cho toàn bộ hệ thống quản lý phòng khám nha khoa:

### 4.1. Danh mục Bảng dữ liệu chính

* **`users` (`DB-TBL-001`)**: Lưu thông tin tài khoản người dùng hệ thống (Quản trị viên, Bác sĩ, Lễ tân).
* **`patients` (`DB-TBL-002`)**: Lưu thông tin hồ sơ bệnh nhân (Họ tên, SĐT, Địa chỉ, Tiền sử bệnh).
* **`doctors` (`DB-TBL-003`)**: Lưu thông tin chuyên môn và lịch làm việc của bác sĩ.
* **`services` (`DB-TBL-004`)**: Lưu danh mục các dịch vụ nha khoa và đơn giá.
* **`appointments` (`DB-TBL-005`)**: Quản lý thông tin đặt lịch hẹn khám giữa bệnh nhân và bác sĩ.
* **`treatments` (`DB-TBL-006`)**: Lưu hồ sơ điều trị, ghi chú lâm sàng và y lệnh của bác sĩ theo từng buổi khám.
* **`invoices` (`DB-TBL-007`)**: Lưu thông tin hóa đơn thanh toán và phương thức giao dịch.
* **`follow_ups` (`DB-TBL-008`)**: Quản lý lịch hẹn tái khám của bệnh nhân.

### 4.2. Cấu trúc chi tiết Bảng `patients` (`DB-TBL-002`)

| Tên cột | Mã trường | Kiểu dữ liệu | PK | FK | Nullable | Mặc định | Mô tả chi tiết |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `id` | DB-FLD-001 | BIGINT | X |  | NO | Auto | Khóa chính định danh bệnh nhân |
| `full_name` | DB-FLD-002 | VARCHAR(255) |  |  | NO |  | Họ và tên đầy đủ của bệnh nhân |
| `phone` | DB-FLD-003 | VARCHAR(20) |  |  | NO |  | Số điện thoại liên hệ |
| `medical_history` | DB-FLD-004 | TEXT |  |  | YES |  | Tiền sử dị ứng hoặc bệnh lý nền |
| `created_at` | DB-FLD-005 | DATETIME |  |  | NO | CURRENT_TIMESTAMP | Thời gian tạo hồ sơ |

---

## 5. KỊCH BẢN KIỂM THỬ (FUNCTIONAL TESTING)

Hệ thống xây dựng bộ kiểm thử bao trùm cả nghiệp vụ quản lý truyền thống lẫn tính năng tích hợp AI:

| Mã TC | UC / REQ Liên kết | Tên Test Case | Điều kiện tiền đề | Các bước thực hiện | Dữ liệu mẫu (Logic) | Kết quả kỳ vọng | Ưu tiên |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **TC-001** | UC-01 / REQ-F-001 | Đăng nhập thành công với vai trò Lễ tân | Tài khoản nhân viên đã được tạo trong hệ thống | 1. Truy cập trang đăng nhập<br>

<br>2. Nhập thông tin tài khoản<br>

<br>3. Nhấn nút Đăng nhập | Username: `letan01`, Password: `Password@123` | Chuyển hướng thành công đến màn hình giao diện Lễ tân | High |
| **TC-002** | UC-04 / REQ-F-004 | Đặt lịch hẹn khám răng thành công | Đã có thông tin bệnh nhân và bác sĩ trong CSDL | 1. Chọn chức năng Đặt lịch<br>

<br>2. Chọn bệnh nhân, bác sĩ, khung giờ trống<br>

<br>3. Xác nhận lưu lịch hẹn | Bệnh nhân: Nguyễn Văn A, Bác sĩ: Dr. Nam, Khung giờ: 09:00 - 09:30 | Tạo lịch hẹn thành công, trạng thái hiển thị "Đã đặt" | High |
| **TC-003** | UC-08 / REQ-F-008 | Kiểm tra tính năng AI tóm tắt điều trị | Bác sĩ đã nhập ghi chú lâm sàng dài | 1. Mở hồ sơ điều trị bệnh nhân<br>

<br>2. Nhấn nút "Tóm tắt bằng AI"<br>

<br>3. Chờ phản hồi hệ thống | Ghi chú khám: "Bệnh nhân đau răng số 46, sâu ngà sâu, đã lấy tủy và hàn tạm..." | Trả về đoạn văn bản tóm tắt ngắn gọn, đúng trọng tâm y lệnh | Medium |

---

## 6. HƯỚNG DẪN SỬ DỤNG HỆ THỐNG (USER GUIDE)

### 6.1. Phân quyền truy cập nhanh

* **Lễ tân**: Thao tác tiếp đón bệnh nhân, quản lý danh sách lịch hẹn, lập hóa đơn và thu tiền dịch vụ.
* **Bác sĩ**: Theo dõi lịch khám trong ngày, cập nhật hồ sơ điều trị răng miệng, sử dụng công cụ AI hỗ trợ tóm tắt ghi chú lâm sàng.
* **Quản trị viên**: Quản lý tài khoản hệ thống, phân quyền người dùng và kiểm soát danh mục dịch vụ nha khoa.

### 6.2. Hướng dẫn thao tác chức năng chính (Step-by-Step)

* **Quy trình Đặt lịch hẹn (`UG-001`)**:
1. Đăng nhập vào hệ thống với tài khoản **Lễ tân**.
2. Chọn mục **Quản lý Lịch hẹn** trên thanh điều hướng bên trái.
3. Nhấn nút **Thêm lịch hẹn mới**, tìm kiếm tên bệnh nhân hoặc thêm mới nếu chưa có hồ sơ.
4. Lựa chọn Bác sĩ phụ trách, dịch vụ khám và khung giờ còn trống trong ngày.
5. Kiểm tra thông tin và nhấn **Xác nhận đặt lịch** để lưu vào cơ sở dữ liệu.



---

## 7. TIÊU CHÍ ĐÁNH GIÁ VÀ NGHIỆM THU ĐỒ ÁN

Báo cáo và sản phẩm phần mềm được đối chiếu theo bộ tiêu chí toàn diện từ Giai đoạn KT1, KT2, KT3 đến Thi hết môn:

* **Tính hoàn thiện chức năng**: Các module quản lý nha khoa và 3 tính năng AI vận hành trơn tru, ổn định.
* **Chất lượng kỹ thuật**: Cấu trúc mã nguồn rõ ràng theo mô hình phân tầng, bảo mật thông tin tuyệt đối qua tệp `.env` và cơ chế ẩn danh dữ liệu cá nhân khi gọi AI.
* **Tính minh chứng trong SDLC**: Lưu trữ đầy đủ nhật ký prompt, tài liệu thiết kế đặc tả, sơ đồ thực thể và kịch bản kiểm thử phục vụ công tác bảo vệ đồ án trước hội đồng.