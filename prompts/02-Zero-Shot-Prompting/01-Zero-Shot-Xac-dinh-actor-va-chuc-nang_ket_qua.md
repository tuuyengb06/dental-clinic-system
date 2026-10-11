# Actor, chức năng và dữ liệu cần bảo vệ

## Bảng actor - mục tiêu - chức năng

| Actor | Mục tiêu | Chức năng phù hợp theo bối cảnh |
|---|---|---|
| Quản trị viên | Quản trị truy cập hệ thống | Đăng nhập; tạo tài khoản nhân viên và gán vai trò. |
| Lễ tân | Tiếp nhận và điều phối bệnh nhân | Đăng nhập; tạo lịch hẹn; cập nhật trạng thái khi bệnh nhân đến; tra cứu thông tin cần thiết theo quyền. |
| Bác sĩ nha khoa | Ghi nhận và xem nghiệp vụ khám | Xem hồ sơ khám theo quyền; ghi nhận thông tin khám; lập kế hoạch điều trị; xác nhận nội dung chuyên môn do AI hỗ trợ. |
| Phụ tá nha khoa | Hỗ trợ quá trình khám/điều trị | Hỗ trợ cập nhật thông tin phục vụ khám và điều trị theo phân quyền; quyền cụ thể chưa được mô tả nên cần xác nhận. |
| Chủ phòng khám | Theo dõi hoạt động | Xem báo cáo hoạt động và doanh thu theo tiêu chí hệ thống cung cấp; quyền lọc/xem chi tiết cần xác nhận. |

## Chức năng và dữ liệu cần bảo vệ quyền truy cập

- Hồ sơ bệnh nhân, thông tin liên hệ, lịch sử khám, ghi chú và hồ sơ sức khỏe: chỉ người có quyền theo vai trò/nghiệp vụ mới được xem hoặc sửa; không suy ra phụ tá/lễ tân có quyền đọc toàn bộ hồ sơ.
- Lịch hẹn có liên kết bệnh nhân: giới hạn trường dữ liệu hiển thị cho từng vai trò; dữ liệu cần cho tiếp nhận không đồng nghĩa quyền đọc ghi chú lâm sàng.
- Hồ sơ khám, kế hoạch điều trị và nội dung chuyên môn do AI hỗ trợ: hạn chế cho bác sĩ/người được cấp quyền; ghi nhận rõ bản AI soạn và bản đã được xem xét nếu hệ thống có hỗ trợ.
- Tài khoản và cấu hình vai trò: chỉ quản trị viên được cấp quyền quản lý; không đưa thông tin xác thực vào đầu ra.
- Báo cáo hoạt động/doanh thu: dùng dữ liệu tổng hợp theo quyền; không kèm định danh bệnh nhân nếu không cần.
- Tìm kiếm/lọc: phải áp dụng quyền ở phía máy chủ, không chỉ ẩn giao diện.

## Đầu ra AI cần nhân viên có thẩm quyền xem xét

- Tóm tắt thông tin khám hoặc nội dung chuyên môn soạn thảo: bác sĩ xem, chỉnh sửa và xác nhận trước khi lưu/sử dụng.
- Chatbot chỉ dùng nội dung FAQ/dịch vụ đã duyệt; không chẩn đoán hoặc quyết định điều trị. Nếu phản hồi trở thành nội dung chuyên môn cá nhân hóa, cần chuyển bác sĩ thay vì cho chatbot tự kết luận.
- Hỏi đáp dữ liệu hoạt động phải tuân theo quyền truy cập của người hỏi; không mặc định cần bác sĩ rà soát báo cáo tổng hợp, trừ khi chính sách dự án quy định.

**Cần làm rõ:** quyền đọc/sửa chi tiết của từng vai trò; ai được tạo tài khoản; ai được xuất báo cáo; định nghĩa và quyền đối với “chủ phòng khám”; cách phê duyệt nội dung AI.
