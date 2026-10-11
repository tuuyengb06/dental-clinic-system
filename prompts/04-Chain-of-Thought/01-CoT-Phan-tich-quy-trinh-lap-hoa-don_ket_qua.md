# Quy trình lập hóa đơn dịch vụ nha khoa

## Phần A: Tóm tắt phân tích

1. **Actor và mục tiêu:** nhân viên được phân quyền lập hóa đơn cho dịch vụ đã được xác nhận; người có quyền ghi nhận thanh toán; bác sĩ/người có thẩm quyền xác nhận dịch vụ chuyên môn. Bệnh nhân là đối tượng của hóa đơn, không mặc định là người thao tác.
2. **Đầu vào:** định danh hồ sơ nội bộ của bệnh nhân; danh sách dịch vụ, số lượng và đơn giá; giảm giá nếu có; phương thức thanh toán; liên kết hồ sơ sử dụng vật tư nếu nghiệp vụ yêu cầu.
3. **Luồng chính:** xác thực quyền → chọn hồ sơ và dịch vụ đã xác nhận → kiểm tra dịch vụ/số lượng/đơn giá → tính tiền theo quy tắc cấu hình → hiển thị để nhân viên kiểm tra → lưu hóa đơn → ghi nhận thanh toán riêng khi có giao dịch → trả trạng thái/kết quả. Mọi thao tác cập nhật liên quan cần đảm bảo nhất quán và chống gửi lặp.
4. **Lỗi/edge case:** hồ sơ/dịch vụ không tồn tại hoặc không được phép; dịch vụ ngừng hoạt động; số lượng/giá không hợp lệ; tổng không khớp; thanh toán thất bại; yêu cầu lưu lặp; vật tư không đủ nếu được ghi nhận trong cùng luồng; hủy hóa đơn đã thanh toán; lỗi giữa các bước.
5. **Đầu ra/hậu điều kiện:** hóa đơn lưu với chi tiết, số tiền và trạng thái; thanh toán có bản ghi trạng thái riêng; tồn kho chỉ đổi theo sự kiện ghi nhận sử dụng vật tư hợp lệ, không tự suy ra từ trạng thái thanh toán. Người dùng chỉ thấy dữ liệu trong phạm vi quyền.
6. **Use case:** chi tiết tại Phần B. Quy tắc chưa được nguồn xác định được đánh dấu để xác nhận, không áp đặt.

## Phần B: Use case “Lập hóa đơn dịch vụ nha khoa”

**Actor chính:** Nhân viên được phân quyền lập hóa đơn.  
**Actor liên quan:** Bác sĩ/người có thẩm quyền xác nhận dịch vụ; nhân viên có quyền ghi nhận thanh toán.  
**Tiền điều kiện:**
- Người dùng đã đăng nhập và có quyền thao tác.
- Hồ sơ liên quan tồn tại và người dùng được phép truy cập.
- Dịch vụ được chọn tồn tại và đã được xác nhận thực hiện/đủ điều kiện lập hóa đơn.

**Luồng chính:**
1. Nhân viên chọn hồ sơ liên quan trong phạm vi quyền.
2. Chọn một hoặc nhiều dịch vụ đã xác nhận; nhập số lượng.
3. Hệ thống kiểm tra trạng thái dịch vụ, số lượng và đơn giá theo dữ liệu được phép.
4. Hệ thống tính tổng/giảm giá theo chính sách đã cấu hình, hiển thị từng dòng và tổng để kiểm tra.
5. Nhân viên xác nhận; hệ thống lưu hóa đơn cùng chi tiết trong thao tác nguyên tử.
6. Nếu có giao dịch thanh toán, người có quyền ghi nhận phương thức/kết quả giao dịch; hóa đơn cập nhật trạng thái theo quy tắc đã xác nhận.
7. Hệ thống trả mã hóa đơn và trạng thái phù hợp; không để lộ trường bệnh nhân không cần thiết.

**Luồng thay thế và lỗi:**
- Dịch vụ/hồ sơ không tồn tại hoặc người dùng không có quyền: từ chối, không ghi thay đổi.
- Dịch vụ không còn hoạt động hoặc chưa được xác nhận: chặn lưu, yêu cầu xác minh.
- Số lượng/đơn giá không hợp lệ hoặc phép tính không khớp: trả lỗi cụ thể, không tạo hóa đơn một phần.
- Thanh toán thất bại: ghi nhận trạng thái thất bại/pending theo chính sách; không báo đã thanh toán.
- Yêu cầu bị gửi lại: dùng mã idempotency hoặc kiểm tra khóa nghiệp vụ để không tạo hóa đơn/giao dịch trùng.
- Vật tư không đủ: nếu thao tác này thật sự ghi nhận sử dụng vật tư thì từ chối/cập nhật nguyên tử theo chính sách kho; không suy ra vật tư đã dùng chỉ từ dòng hóa đơn.
- Hủy hóa đơn đã thanh toán: chuyển theo luồng hủy/điều chỉnh được duyệt; việc hoàn tiền và hoàn vật tư là quyết định riêng.
- Lỗi khi lưu bất kỳ thành phần nào: rollback toàn bộ cập nhật trong cùng giao dịch; nếu nhà cung cấp thanh toán ngoài hệ thống, cần quy trình đối soát riêng.

**Hậu điều kiện:** hóa đơn và các dòng được lưu nhất quán; giao dịch thanh toán phản ánh kết quả quan sát được; lịch sử vật tư chỉ thay đổi khi có bản ghi sử dụng hợp lệ. Có thể ghi audit tối thiểu theo chính sách, không log hồ sơ/định danh thừa.

## Phần C: Các điểm cần kiểm thử

- Nhân viên có quyền tạo hóa đơn hợp lệ; người không quyền bị từ chối.
- Dịch vụ không tồn tại/ngừng hoạt động và số lượng bằng 0 hoặc âm.
- Tổng tiền, giảm giá, làm tròn/đơn vị tiền và dữ liệu thiếu hoặc không khớp.
- Thanh toán thành công, thất bại, timeout và phản hồi lặp.
- Hai yêu cầu tạo đồng thời hoặc gửi lại không tạo bản ghi trùng.
- Lỗi giữa khi lưu hóa đơn/chi tiết/thanh toán khiến transaction rollback.
- Vật tư không đủ; chỉ cập nhật khi nghiệp vụ ghi nhận sử dụng, không khi thanh toán đơn thuần.
- Hủy hóa đơn chưa thanh toán/đã thanh toán; kiểm tra quyền, trạng thái, hoàn tiền/hoàn vật tư theo chính sách đã xác nhận.
- Vai trò không đủ quyền không thấy hồ sơ, ghi chú sức khỏe hoặc dữ liệu giao dịch không cần thiết.

**Cần xác nhận:** công thức gross/net, chính sách giảm giá và làm tròn, trạng thái hợp lệ, cách xử lý hoàn tiền/hủy, thời điểm ghi nhận vật tư, và mô hình tích hợp thanh toán.
