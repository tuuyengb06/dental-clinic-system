# So sánh prompt cơ bản và prompt có cấu trúc

| Tiêu chí | Prompt A | Prompt B | Nhận xét |
|---|---|---|---|
| Instructions | Yêu cầu chung: thống kê doanh thu tháng này | Chỉ rõ vai trò, SQLite, doanh thu theo ngày trong tháng hiện tại | B xác định nhiệm vụ và phạm vi rõ hơn; “tháng hiện tại” vẫn phụ thuộc ngày chạy và timezone |
| Context | Không có | Nêu phòng khám nha khoa | B có ngữ cảnh, nhưng phần lớn tính đúng đắn đến từ schema và quy tắc |
| Input Data | Không nêu bảng/cột | Đưa invoices với các cột dùng được | A buộc mô hình đoán schema; B cho dữ liệu đầu vào cụ thể |
| DBMS | Không nêu | SQLite | B tránh cú pháp đặc thù DBMS không phù hợp |
| Điều kiện lọc | Không nêu trạng thái hoặc thời gian chính xác | Chỉ `status='paid'`; lọc theo tháng hiện tại | B giảm nhầm lẫn giữa doanh thu đã thanh toán và hóa đơn khác trạng thái |
| Tính toán | Không định nghĩa doanh thu | `gross_revenue=total_amount`, `net_revenue=total_amount-discount_amount` | B định nghĩa phép tính, nhưng phải xác minh `total_amount` thực sự là trước giảm giá và xử lý `discount_amount IS NULL` |
| Grain/nhóm | “thống kê doanh thu” không nói theo ngày hay tổng | Theo ngày | B xác định cấp độ tổng hợp |
| Dữ liệu riêng tư | Không giới hạn join | Cấm nối patients và trả dữ liệu định danh | B giảm truy cập dữ liệu không cần thiết |
| Output | Không quy định | Chỉ SQL và giải thích ngắn giả định | B kiểm soát định dạng đầu ra |
| Giả định | Không yêu cầu nêu | Yêu cầu giải thích giả định | B hỗ trợ review, nhưng vẫn cần đối chiếu lược đồ/thực tế |
| Rủi ro dùng thực tế | Có thể tạo SQL sai schema, sai kỳ, sai định nghĩa doanh thu hoặc truy vấn dư dữ liệu bệnh nhân | Ít mơ hồ hơn nhưng SQL vẫn cần kiểm thử, xác minh cột/ngày và chính sách kế toán | Cấu trúc tốt không thay thế kiểm thử hay xác nhận nghiệp vụ |

## Kết luận cho sinh viên

Prompt A quá ngắn nên không xác định được hệ quản trị, bảng, cách tính doanh thu, trạng thái hóa đơn hay mức độ tổng hợp. Mô hình có thể tự đoán các chi tiết này và tạo truy vấn trông hợp lý nhưng sai nghiệp vụ. Prompt B thu hẹp phần lớn mơ hồ bằng schema, điều kiện thanh toán, cột đầu ra và giới hạn dữ liệu bệnh nhân. Tuy vậy, cần xác nhận định nghĩa `total_amount`, ý nghĩa “tháng hiện tại”, định dạng ngày và timezone của dữ liệu thật. Cũng cần kiểm tra giá trị `discount_amount` NULL và khả năng dữ liệu đầu vào có bất thường. Không nên coi SQL sinh ra là đúng chỉ vì prompt chi tiết; hãy review schema, chạy test với dữ liệu giả lập và kiểm tra kết quả tổng hợp.
