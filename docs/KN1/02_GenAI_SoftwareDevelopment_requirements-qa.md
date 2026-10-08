# 1. TỔNG QUAN VỀ HOẠT ĐỘNG CLARIFICATION

## 1.1. Mục tiêu của hoạt động làm rõ yêu cầu
Tài liệu này được xây dựng để làm rõ các điểm mờ, thiếu thông tin hoặc cần xác nhận trước khi chuyển sang giai đoạn đặc tả yêu cầu chi tiết. Dữ liệu đầu vào được kế thừa từ project.md, informember.md và 01_GenAI_SoftwareDevelopment_project-plan.md, nhằm đảm bảo các ranh giới nghiệp vụ, quyền truy cập, kịch bản ngoại lệ và yêu cầu phi chức năng được xác nhận rõ hơn.

## 1.2. Bối cảnh cần clarifying
Dự án tập trung vào hệ thống quản lý nha khoa có tích hợp AI với các nghiệp vụ chính: quản lý bệnh nhân, bác sĩ, lịch hẹn, hồ sơ điều trị, dịch vụ, thanh toán, lịch tái khám và AI hỗ trợ tóm tắt điều trị, nhắc tái khám, giải thích dịch vụ. Tuy nhiên, từ các tài liệu đầu vào, vẫn còn các điểm cần làm rõ để tránh hiểu lệch ở bước thiết kế và phát triển sau này.

## 1.3. Cách tiếp cận làm rõ yêu cầu
- Xác định các điểm mơ hồ theo 7 nhóm chính: nghiệp vụ, actor, chức năng, quy tắc nghiệp vụ, ngoại lệ, phi chức năng, tích hợp AI.
- Chỉ ghi nhận các câu hỏi cần xác minh để tránh đưa ra quyết định chưa có căn cứ.
- Các câu hỏi chưa có câu trả lời chính thức trong tài liệu sẽ giữ trạng thái "Chưa trả lời".

# 2. BẢNG TIẾP NHẬN VÀ XỬ LÝ CÂU HỎI (Q&A MATRIX)

| Mã câu hỏi | Nhóm câu hỏi | Nội dung câu hỏi | Nguồn phát sinh | Trạng thái | Câu trả lời / Phản hồi | Ảnh hưởng nếu chưa trả lời |
|---|---|---|---|---|---|---|
| QA-BUS-001 | Nghiệp vụ | Quy trình chính xác từ khi bệnh nhân đặt lịch đến khi hoàn tất thanh toán và tái khám là gì? | project.md | Chưa trả lời | *[Chờ phản hồi]* | Nghiêm trọng |
| QA-BUS-002 | Nghiệp vụ | Có cần quy trình khác biệt giữa khám định kỳ, khám điều trị và khám khẩn cấp không? | project.md | Chưa trả lời | *[Chờ phản hồi]* | Nghiêm trọng |
| QA-BUS-003 | Nghiệp vụ | Trạng thái lịch hẹn cần có các trạng thái nào (đã đặt, xác nhận, hoàn thành, hủy, từ chối, tái khám)? | project.md | Chưa trả lời | *[Chờ phản hồi]* | Nghiêm trọng |
| QA-ACT-001 | Phân quyền | Vai trò nào được phép tạo/sửa/xóa thông tin bệnh nhân, bác sĩ và dịch vụ? | project.md | Đã trả lời | Theo project.md, hệ thống có phân quyền chi tiết cho Quản trị viên, Bác sĩ và Lễ tân. Cần xác nhận quyền cụ thể từng hành động. | Trung bình |
| QA-ACT-002 | Phân quyền | Bệnh nhân có truy cập trực tiếp hệ thống hay chỉ nhận thông tin qua nhân sự/phòng khám? | project.md | Chưa trả lời | *[Chờ phản hồi]* | Trung bình |
| QA-ACT-003 | Phân quyền | Vai trò Quản trị viên có quyền xem toàn bộ hồ sơ y tế của bệnh nhân hay chỉ xem báo cáo/điều hành? | project.md | Chưa trả lời | *[Chờ phản hồi]* | Nghiêm trọng |
| QA-FUN-001 | Chức năng chi tiết | Hệ thống cần tính toán doanh thu theo ngày, tháng, bác sĩ, dịch vụ hay theo từng hóa đơn? | project.md | Chưa trả lời | *[Chờ phản hồi]* | Trung bình |
| QA-FUN-002 | Chức năng chi tiết | Dữ liệu đầu vào của AI gồm những trường nào khi tóm tắt điều trị và nhắc tái khám? | project.md | Đã trả lời | Theo project.md, đầu vào AI bao gồm ghi chú khám bệnh của bác sĩ, thông tin lịch hẹn tái khám và câu hỏi/đề nghị giải thích dịch vụ. | Trung bình |
| QA-FUN-003 | Chức năng chi tiết | Hệ thống có yêu cầu kiểm tra trùng lịch bác sĩ theo khung giờ, ngày, ca trực hay cả hai? | project.md | Đã trả lời | project.md nêu rõ: quản lý lịch hẹn cần tránh trùng lặp khung giờ của bác sĩ. Cần xác định chi tiết ràng buộc thời gian. | Nghiêm trọng |
| QA-FUN-004 | Chức năng chi tiết | Mức giảm giá/chiết khấu hoặc các chính sách thanh toán có quy định cụ thể không? | project.md | Chưa trả lời | *[Chờ phản hồi]* | Trung bình |
| QA-RULE-001 | Quy tắc nghiệp vụ | Có quy tắc nào bắt buộc bác sĩ phải cập nhật y lệnh hoặc ghi chú điều trị trước khi kết thúc cuộc hẹn không? | project.md | Chưa trả lời | *[Chờ phản hồi]* | Nghiêm trọng |
| QA-RULE-002 | Quy tắc nghiệp vụ | Quy tắc khóa lịch hẹn, hủy lịch, đổi lịch và tái khám có thời hạn tối đa hay không? | project.md | Chưa trả lời | *[Chờ phản hồi]* | Trung bình |
| QA-RULE-003 | Quy tắc nghiệp vụ | Có cần xác thực dữ liệu như số điện thoại, lịch hẹn, dị ứng thuốc, mục bệnh lý trước khi lưu vào hệ thống không? | project.md | Đã trả lời | project.md có nêu ví dụ bệnh nhân có tiền sử dị ứng penicillin; điều này cho thấy dữ liệu bệnh lý và thông tin cá nhân cần được lưu và kiểm tra hợp lệ. | Trung bình |
| QA-EXC-001 | Ngoại lệ & Kịch bản lỗi | Khi bác sĩ hoặc lễ tân nhập dữ liệu không hợp lệ, hệ thống cần xử lý như thế nào? | project.md | Chưa trả lời | *[Chờ phản hồi]* | Nghiêm trọng |
| QA-EXC-002 | Ngoại lệ & Kịch bản lỗi | Nếu bệnh nhân hủy lịch sau khi đã xác nhận, hệ thống cần giữ lịch sử hay xóa hoàn toàn dữ liệu? | project.md | Chưa trả lời | *[Chờ phản hồi]* | Trung bình |
| QA-EXC-003 | Ngoại lệ & Kịch bản lỗi | Nếu hệ thống AI timeout, trả về rỗng hoặc sai định dạng, người dùng cần nhận thông báo nào? | project.md | Đã trả lời | project.md nêu rõ AI cần xử lý lỗi như timeout, giới hạn tần suất gọi và phản hồi sai định dạng JSON trong giai đoạn phát triển. Cần xác định quy trình hiện thực chi tiết. | Nghiêm trọng |
| QA-NFR-001 | Phi chức năng | Yêu cầu về bảo mật, quyền riêng tư dữ liệu y tế bệnh nhân và API key là gì? | project.md | Đã trả lời | project.md nêu rõ API key đặt trong .env và không gửi thông tin định danh nhạy cảm khi không cần thiết. | Nghiêm trọng |
| QA-NFR-002 | Phi chức năng | Mức độ sẵn sàng, hiệu năng phản hồi và số lượng người dùng demo cần đáp ứng là bao nhiêu? | project.md | Chưa trả lời | *[Chờ phản hồi]* | Trung bình |
| QA-NFR-003 | Phi chức năng | Hệ thống demo cần hỗ trợ lưu trữ dữ liệu ở quy mô bao nhiêu (số bệnh nhân, lịch hẹn, dịch vụ, hóa đơn)? | project.md | Chưa trả lời | *[Chờ phản hồi]* | Trung bình |
| QA-AI-001 | Tích hợp & AI | Mô hình AI nào được chọn và mức độ kiểm soát cảnh báo y tế là gì? | project.md | Đã trả lời | project.md cho biết AI Engine có thể là OpenAI API, Gemini API, Claude API, Hugging Face hoặc Ollama, nhưng chưa quyết định cụ thể. | Nghiêm trọng |
| QA-AI-002 | Tích hợp & AI | AI có cần lưu nhật ký prompt và phản hồi để đánh giá độ tin cậy không? | project.md | Đã trả lời | project.md nêu rõ lưu trữ nhật ký prompt và phản hồi của AI làm minh chứng trong thư mục tài liệu dự án. | Trung bình |
| QA-AI-003 | Tích hợp & AI | Mức độ an toàn khi AI giải thích dịch vụ là gì: chỉ giải thích, hoặc có yêu cầu nhắc cảnh báo bắt buộc với bệnh nhân? | project.md | Đã trả lời | project.md nhấn mạnh rằng giải thích dịch vụ phải đi kèm cảnh báo rõ ràng, không thay thế chẩn đoán của bác sĩ, chỉ mang tính tham khảo. | Nghiêm trọng |

# 3. TỔNG HỢP CÁC ĐIỂM NGHẼN KỸ THUẬT & ĐỀ XUẤT CÓ ĐIỀU KIỆN

## 3.1. Các điểm nghẽn kỹ thuật cần làm rõ trước khi thiết kế
1. Quy trình nghiệp vụ chi tiết từ đặt lịch đến thanh toán, tái khám và xử lý hoàn trả hoặc hủy lịch chưa được mô tả đầy đủ.
2. Ràng buộc quyền truy cập theo từng chức năng của từng vai trò chưa được định nghĩa chi tiết cho từng màn hình hoặc API.
3. Dữ liệu y tế cần có quy tắc validate rõ ràng hơn về thời gian, tiền sử bệnh lý, dị ứng thuốc, lịch sử điều trị và trạng thái hủy/phản hồi.
4. Chưa xác định cụ thể phương án AI engine và định dạng phản hồi chuẩn để tích hợp vào hệ thống.
5. Chưa có thông tin rõ về ưu tiên xử lý ngoại lệ, lưu lịch sử dữ liệu và thông báo lỗi tới người dùng.

## 3.2. Đề xuất có điều kiện
- Có điều kiện xác nhận mô hình nghiệp vụ thực tế của phòng khám: lịch hẹn có thể chia thành các trạng thái rõ ràng và quy trình thay đổi theo từng loại khám.
- Có điều kiện xác định rõ khả năng truy cập của từng vai trò, đặc biệt quyền xem/sửa/xóa hồ sơ y tế và báo cáo doanh thu.
- Có điều kiện xác định cơ chế bảo mật cho dữ liệu bệnh nhân, bao gồm lưu trữ, truy xuất và xử lý khi gọi AI.
- Có điều kiện thống nhất AI provider và định dạng phản hồi chuẩn để reduce lỗi, đảm bảo cảnh báo y tế và kiểm soát đầu vào.
- Có điều kiện bổ sung các kịch bản lỗi chi tiết trước khi chuyển sang thiết kế chức năng và database.

## 3.3. Kết luận
Các tài liệu đầu vào đã xác định được bối cảnh, mục tiêu, vai trò và phạm vi tổng thể của hệ thống quản lý nha khoa có tích hợp AI. Tuy nhiên, để hoàn thiện đặc tả yêu cầu ở bước sau, cần làm rõ thêm các quy trình nghiệp vụ, quyền truy cập, quy tắc dữ liệu, ràng buộc ngoại lệ, yêu cầu phi chức năng và lựa chọn công nghệ AI cụ thể. Với các câu hỏi trên, nhóm có thể tập trung vào việc xác nhận trước khi chuyển sang giai đoạn thiết kế sâu hơn.
