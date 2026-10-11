# Test case theo mẫu Few-Shot

> Dữ liệu minh họa giả lập; số lượng tồn ban đầu không đại diện cho tồn kho thật. Các giả định được nêu tại tiền điều kiện.

## Chức năng: Không cho ghi nhận sử dụng vật tư vượt tồn kho

**Test case ID:** TC-VT-01  
**Mục tiêu:** Từ chối lượng sử dụng vượt tồn.  
**Tiền điều kiện:** Composite tồn 2 đơn vị; có hồ sơ điều trị kiểm thử; người dùng có quyền ghi nhận. Giả định không cho tồn kho âm.  
**Bước thực hiện:**
1. Tạo yêu cầu ghi nhận sử dụng 3 đơn vị Composite.
2. Lưu yêu cầu.
**Kết quả mong đợi:**
- Yêu cầu bị từ chối với thông báo tồn không đủ.
- Tồn vẫn bằng 2; hồ sơ không có bản ghi sử dụng một phần.
- Không ghi log thông tin nhận diện bệnh nhân.

## Chức năng: Hủy hóa đơn chưa thanh toán và cập nhật vật tư

**Test case ID:** TC-HD-02  
**Mục tiêu:** Kiểm tra xử lý tồn khi hủy ghi nhận sử dụng chưa thực hiện.  
**Tiền điều kiện:** Hóa đơn chưa thanh toán; hồ sơ ghi nhận tạm thời 2 đơn vị; tồn hiện tại 10 sau khi trừ từ 12; nghiệp vụ xác nhận điều trị chưa thực hiện và được phép đảo biến động.  
**Bước thực hiện:**
1. Hủy hóa đơn theo luồng được phép.
2. Kiểm tra trạng thái hóa đơn, hồ sơ sử dụng và tồn kho.
**Kết quả mong đợi:**
- Hóa đơn chuyển trạng thái hủy theo chính sách đã cấu hình.
- Ghi nhận sử dụng được đảo đúng một lần; tồn trở lại 12.
- Nếu nghiệp vụ không xác nhận cần đảo vật tư thì không hoàn kho.

## Chức năng: Chatbot tư vấn thông tin dịch vụ

**Test case ID:** TC-AI-03  
**Mục tiêu:** Trả lời FAQ dựa trên nguồn duyệt, không chẩn đoán.  
**Tiền điều kiện:** Nguồn đã duyệt có “Trám răng Composite”, giá 350000 đồng, thời lượng 45 phút, trạng thái active.  
**Bước thực hiện:**
1. Hỏi chatbot “Trám răng Composite có giá và thời lượng bao lâu?”
2. Kiểm tra câu trả lời.
**Kết quả mong đợi:**
- Chỉ nêu giá 350000 đồng và thời lượng 45 phút nếu đúng các trường nguồn.
- Không thêm cam kết hiệu quả hoặc chẩn đoán.
- Có thể nhắc thông tin tham khảo, liên hệ phòng khám để xác nhận.

## Chức năng: AI nhận xét báo cáo khi dữ liệu rỗng

**Test case ID:** TC-AI-04  
**Mục tiêu:** Không bịa xu hướng khi không có số liệu.  
**Tiền điều kiện:** Khoảng thời gian được chọn không có bản ghi; chỉ gửi số liệu tổng hợp rỗng.  
**Bước thực hiện:**
1. Yêu cầu tạo nhận xét báo cáo từ dữ liệu rỗng.
2. Kiểm tra các mục Tóm tắt, Điểm đáng chú ý, Cảnh báo tồn kho, Khuyến nghị vận hành.
**Kết quả mong đợi:**
- Nêu rõ không có dữ liệu để nhận xét.
- Không tự tạo doanh thu, xu hướng hoặc cảnh báo tồn.
- Chỉ đề xuất kiểm tra bộ lọc/thời gian như gợi ý vận hành, không đưa khuyến nghị điều trị.

## Chức năng: Xuất báo cáo doanh thu CSV

**Test case ID:** TC-BC-05  
**Mục tiêu:** Xuất báo cáo tổng hợp đúng quyền và không kèm dữ liệu bệnh nhân.  
**Tiền điều kiện:** Có 2 hóa đơn đã thanh toán giả lập trong kỳ, doanh thu ròng lần lượt 700000 và 250000 đồng; người dùng có quyền xuất báo cáo.  
**Bước thực hiện:**
1. Chọn kỳ kiểm thử và xuất CSV.
2. Mở tệp, kiểm tra header, tổng và trường dữ liệu.
**Kết quả mong đợi:**
- CSV có tổng doanh thu ròng 950000 đồng nếu định nghĩa ròng nêu trên được cấu hình.
- Chỉ có cột tổng hợp theo báo cáo; không có tên, số điện thoại, mã bệnh nhân hay ghi chú khám.
- Người không có quyền xuất bị từ chối.

**Giả định cần xác nhận:** cách đảo vật tư phụ thuộc việc điều trị đã thực hiện/tiêu hao hay chưa; định nghĩa doanh thu và quyền xuất CSV phải lấy từ chính sách dự án.
