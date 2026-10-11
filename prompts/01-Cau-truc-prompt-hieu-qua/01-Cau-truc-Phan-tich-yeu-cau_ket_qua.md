# Phân tích yêu cầu hệ thống quản lý nha khoa tích hợp AI

## 1. Bối cảnh và vấn đề

Phòng khám cần quản lý bệnh nhân, lịch hẹn, hồ sơ khám/điều trị, dịch vụ, kế hoạch điều trị, hóa đơn, thanh toán, vật tư và báo cáo. Quản lý bằng sổ hoặc bảng tính rời rạc dễ gây sai sót khi xếp lịch, khó tra cứu lịch sử và tốn thời gian tổng hợp hoạt động, doanh thu.

Tài liệu `docs/KN1/project.md` mô tả thêm quản lý bác sĩ, lịch tái khám, tránh trùng lịch bác sĩ, nhắc tái khám và giải thích dịch vụ bằng AI. Tài liệu này nêu vai trò Quản trị viên, Bác sĩ, Lễ tân; prompt hiện tại còn nêu Phụ tá nha khoa và Chủ phòng khám. Cần xác nhận danh sách actor/quyền chính thức và phân biệt “chủ phòng khám” có vai trò riêng hay thuộc nhóm quản trị.

## 2. Mục tiêu hệ thống

- Tập trung dữ liệu và quy trình vận hành phòng khám.
- Hỗ trợ nhân viên tiếp nhận, đặt lịch; hỗ trợ bác sĩ xem hồ sơ và ghi nhận nghiệp vụ chuyên môn; hỗ trợ chủ phòng khám theo dõi báo cáo theo quyền được cấp.
- Cung cấp chatbot cho câu hỏi thường gặp dựa trên nội dung đã duyệt; hỗ trợ tóm tắt/soạn thảo để người có thẩm quyền kiểm tra; hỏi đáp dữ liệu tổng hợp theo quyền.
- AI chỉ hỗ trợ, không chẩn đoán, chỉ định điều trị hoặc thay thế quyết định bác sĩ. Dữ liệu chuyên môn AI soạn phải được bác sĩ/người có thẩm quyền xem xét trước khi dùng.

## 3. Actor và nhu cầu

| Actor | Mục tiêu / nhu cầu | Chức năng liên quan |
|---|---|---|
| Quản trị viên | Quản lý người dùng và vận hành hệ thống | Đăng nhập, phân quyền, cấu hình; phạm vi cấu hình chi tiết cần xác nhận |
| Lễ tân | Tiếp nhận và điều phối lịch | Tra cứu hồ sơ tối thiểu theo quyền, tạo/cập nhật lịch hẹn, hỗ trợ tiếp nhận |
| Bác sĩ nha khoa | Quản lý công việc khám và nội dung chuyên môn | Xem hồ sơ theo quyền, ghi nhận khám, lập kế hoạch điều trị, xem/chỉnh sửa/xác nhận nội dung AI hỗ trợ |
| Phụ tá nha khoa | Hỗ trợ quá trình khám/điều trị | Cập nhật thông tin được phân công; quyền xem/sửa từng loại dữ liệu cần xác nhận |
| Chủ phòng khám | Theo dõi hoạt động | Xem báo cáo tổng hợp, doanh thu; bộ lọc và quyền chi tiết cần xác nhận |

## 4. Danh sách chức năng quản lý

| Chức năng | Mục tiêu | Actor liên quan |
|---|---|---|
| Đăng nhập và phân quyền | Chỉ cho người dùng hợp lệ truy cập chức năng/dữ liệu được cấp | Tất cả; Quản trị viên quản lý vai trò |
| Quản lý hồ sơ bệnh nhân | Lưu thông tin cần thiết và lịch sử khám | Lễ tân, Bác sĩ, Phụ tá theo quyền; chi tiết quyền cần xác nhận |
| Quản lý lịch hẹn | Tạo, cập nhật trạng thái và phân công lịch | Lễ tân, Bác sĩ; ràng buộc tránh trùng lịch cần xác nhận theo tài liệu dự án |
| Hồ sơ khám/điều trị | Ghi nhận tình trạng răng, ghi chú, dịch vụ thực hiện | Bác sĩ; Phụ tá hỗ trợ trong phạm vi được cấp |
| Danh mục dịch vụ | Quản lý mã, tên, mô tả, giá, trạng thái | Nhân viên được phân quyền; vai trò cụ thể cần xác nhận |
| Kế hoạch điều trị | Lưu kế hoạch do bác sĩ lập/xác nhận | Bác sĩ |
| Hóa đơn và thanh toán | Ghi dịch vụ, số lượng, giảm giá nếu có, tổng tiền và giao dịch | Nhân viên có quyền; người được phép hủy/điều chỉnh và quy trình cần xác nhận |
| Quản lý vật tư | Theo dõi mã, tên, đơn vị, tồn và trạng thái | Nhân viên được phân quyền; nhập/xuất/kiểm kê chỉ xác định theo nghiệp vụ đã duyệt |
| Báo cáo | Tổng hợp lịch hẹn, lượt khám, doanh thu, dịch vụ, vật tư | Chủ phòng khám và vai trò được cấp quyền |

## 5. Danh sách chức năng AI

| Chức năng | Mục tiêu / giới hạn | Actor |
|---|---|---|
| Chatbot dịch vụ và lịch hẹn | Trả lời FAQ từ nội dung phòng khám phê duyệt; không bịa, không chẩn đoán hay cá nhân hóa điều trị | Khách/người dùng; actor khách hàng cần xác nhận trong phân quyền dự án |
| Tóm tắt/soạn thảo nội dung khám | Giúp bác sĩ rà soát nhanh; chỉ dùng dữ liệu được phép, không tự chẩn đoán; bác sĩ phải xem và xác nhận | Bác sĩ |
| Hỏi đáp dữ liệu hoạt động | Truy vấn/tóm tắt dữ liệu tổng hợp trong phạm vi quyền của người hỏi | Chủ phòng khám/người dùng được cấp quyền |

## 6. Dữ liệu chính

- Người dùng, vai trò và cấu hình quyền.
- Bệnh nhân: mã và thông tin liên hệ; lịch sử khám, tiền sử do bệnh nhân cung cấp, lịch sử điều trị (dữ liệu nhạy cảm, truy cập hạn chế).
- Lịch hẹn: bệnh nhân, thời gian, nhu cầu/dịch vụ, nhân viên phụ trách, trạng thái.
- Hồ sơ khám: tình trạng răng, ghi chú chuyên môn, dịch vụ thực hiện, kế hoạch điều trị.
- Dịch vụ: mã, tên, mô tả, giá, trạng thái.
- Hóa đơn/chi tiết/thanh toán: dịch vụ, số lượng, giảm giá nếu có, tổng tiền, phương thức và thông tin giao dịch cần thiết.
- Vật tư: mã, tên, đơn vị, tồn, trạng thái; biến động kho chỉ thiết kế khi nghiệp vụ nguồn xác nhận.
- Dữ liệu báo cáo tổng hợp; nên tách khỏi dữ liệu định danh/hồ sơ sức khỏe khi không cần thiết.

## 7. Yêu cầu phi chức năng

- **Bảo mật và quyền riêng tư:** phân quyền theo vai trò/từng thao tác; giới hạn xem hồ sơ bệnh nhân và hồ sơ khám; không gửi định danh hoặc dữ liệu sức khỏe đến AI nếu không cần.
- **An toàn AI:** bám nguồn đã duyệt; nêu thiếu dữ liệu; nội dung chuyên môn cần người có thẩm quyền duyệt; AI không tự ra quyết định điều trị.
- **Toàn vẹn dữ liệu:** kiểm tra tính hợp lệ và đảm bảo cập nhật hóa đơn, thanh toán, hồ sơ sử dụng vật tư nhất quán; chi tiết transaction/quy tắc nghiệp vụ cần xác nhận.
- **Khả năng sử dụng:** luồng thao tác phù hợp lễ tân/bác sĩ, thông báo lỗi rõ ràng.
- **Khả năng kiểm thử/bảo trì:** có dữ liệu giả lập, kiểm thử các luồng chính và ngoại lệ; tách prompt khỏi mã nguồn theo tài liệu dự án.
- **Hiệu năng, khả dụng, lưu trữ và thời hạn lưu dữ liệu:** chưa có ngưỡng/chính sách được xác nhận, cần thống nhất.

## 8. Rủi ro và giả định cần kiểm chứng

1. **Phạm vi actor khác nhau:** tài liệu `project.md` liệt kê Quản trị viên, Bác sĩ, Lễ tân; prompt thêm Phụ tá và Chủ phòng khám. Cần chốt actor, ma trận quyền và liệu có actor bệnh nhân/khách dùng chatbot.
2. **Phạm vi nghiệp vụ khác nhau:** nguồn dự án đề cập quản lý bác sĩ, lịch tái khám, nhắc lịch, nhưng prompt hiện tại không yêu cầu rõ các mục này. Cần xác nhận phạm vi phiên bản.
3. **Vật tư:** mô tả prompt chỉ xác nhận theo dõi cơ bản; không suy ra quy trình nhập/xuất/kiểm kê hay thời điểm trừ tồn.
4. **Hủy hóa đơn, hoàn tiền và hoàn kho:** chính sách, quyền, tính lặp lại và mối liên hệ với dịch vụ đã thực hiện cần được phòng khám xác nhận.
5. **AI và dữ liệu nhạy cảm:** xác định mục đích, sự đồng ý, nơi xử lý, thời gian lưu, khử định danh, nhật ký và cách kiểm soát nhà cung cấp AI; đây là câu hỏi cần xác minh, không phải kết luận pháp lý.
6. **Doanh thu:** cần định nghĩa doanh thu gộp/ròng, thời điểm ghi nhận, giảm giá, hoàn/điều chỉnh và múi giờ báo cáo.
7. **Giả định:** bảng/entity liệt kê ở trên là khung ban đầu dựa trên mô tả; mọi quyền, trạng thái, ràng buộc hoặc quy tắc chưa nêu phải được xác nhận trước triển khai.
