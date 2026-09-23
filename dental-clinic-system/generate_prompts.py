import os

root = os.path.join('.', 'prompts')
os.makedirs(root, exist_ok=True)

folders = [
    '01-Cau-truc-prompt-hieu-qua',
    '02-Zero-Shot-Prompting',
    '03-Few-Shot-Prompting',
    '04-Chain-of-Thought',
    '05-Self-Consistency',
    '06-ReAct',
    '07-RAG',
    '08-Sinh-ma-nguon',
    '09-Prompt-cho-go-loi',
    '10-Prompt-cho-sinh-kien-thu',
    '11-Prompt-cho-viet-tai-lieu',
    '12-Prompt-cho-tac-vu-lap-trinh-nang-cao',
    '13-Chu-trinh-quant-ly',
    '14-Kiem-thu-va-tinh-chinh',
    '15-Bao-mat-prompt',
]

contents = {
    '01-Cau-truc-prompt-hieu-qua': '''# 01-Cau-truc-prompt-hieu-qua\n\nMẫu prompt áp dụng trong dự án Dental Management System:\n\n```text\nBạn là Product Owner và kỹ sư phần mềm cho hệ thống Dental Management System.\nHãy phân tích yêu cầu cho hệ thống quản lý phòng khám nha khoa với các chức năng: đặt lịch hẹn, hồ sơ bệnh nhân, lịch làm việc bác sĩ, thanh toán, hồ sơ điều trị, báo cáo doanh thu.\nYêu cầu đầu ra:\n1. Liệt kê các user story.\n2. Chỉ rõ các chức năng chính.\n3. Mô tả Actor, Use case, input/output.\n4. Đưa ra mô hình dữ liệu chính.\n\nVới mỗi module, hãy nêu rõ ràng, ngắn gọn và không mơ hồ.\n```\n''',
    '02-Zero-Shot-Prompting': '''# 02-Zero-Shot-Prompting\n\nMẫu prompt áp dụng trong dự án Dental Management System:\n\n```text\nHãy thiết kế một chiến lược tự động hóa đặt lịch hẹn trong hệ thống Dental Management System cho bệnh nhân và bác sĩ.\nYêu cầu: xác định mục tiêu, luồng đặt lịch, nhắc lịch hẹn, kiểm tra xung đột lịch, và lưu trữ lịch sử đặt hẹn.\nViết một bản kế hoạch ngắn theo mô hình lưu trữ dữ liệu, quy trình nghiệp vụ, và giao diện người dùng.\n```\n''',
    '03-Few-Shot-Prompting': '''# 03-Few-Shot-Prompting\n\nMẫu prompt áp dụng trong dự án Dental Management System:\n\n```text\nHãy phân loại phản hồi khách hàng của phòng khám nha khoa theo ba nhãn: POSITIVE, NEGATIVE, REQUEST.\nVí dụ: \n- "Tôi hài lòng vì bác sĩ giải thích rõ ràng" -> POSITIVE\n- "Lịch hẹn bị trễ" -> NEGATIVE\n- "Tôi muốn đặt lịch tái khám" -> REQUEST\n\nBây giờ hãy phân loại các câu phản hồi sau cho hệ thống Dental Management System:\n1. Tôi muốn đổi giờ hẹn sang ngày mai.\n2. Bác sĩ rất thân thiện và chuyên nghiệp.\n3. Tôi thấy khu vực chờ khá chật.\n```\n''',
    '04-Chain-of-Thought': '''# 04-Chain-of-Thought\n\nMẫu prompt áp dụng trong dự án Dental Management System:\n\n```text\nHãy phân tích nguyên nhân vì sao hệ thống đặt lịch hẹn của Dental Management System không cho phép bác sĩ A nhận lịch hẹn từ bệnh nhân.\nHãy suy luận từng bước: kiểm tra dữ liệu bệnh nhân, kiểm tra lịch làm việc bác sĩ, kiểm tra địa điểm khám, kiểm tra trạng thái tài khoản, kiểm tra quy tắc xác nhận lịch hẹn.\nSau đó đưa ra giải pháp cụ thể từng bước và mô tả kết quả mong đợi.\n```\n''',
    '05-Self-Consistency': '''# 05-Self-Consistency\n\nMẫu prompt áp dụng trong dự án Dental Management System:\n\n```text\nHãy đề xuất tối thiểu 03 phương án tối ưu cho phần lịch hẹn trong Dental Management System.\nVới mỗi phương án, nêu ưu điểm, nhược điểm, rủi ro và mức độ khó triển khai.\nSau đó chọn phương án tốt nhất dựa trên tiêu chí: dễ sử dụng, dễ bảo trì, dữ liệu rõ ràng, phù hợp quy trình phòng khám nha khoa.\n```\n''',
    '06-ReAct': '''# 06-ReAct\n\nMẫu prompt áp dụng trong dự án Dental Management System:\n\n```text\nBạn là trợ lý phát triển hệ thống Dental Management System.\nHãy theo quy trình Reasoning-Action: \n1. Phân tích vấn đề về lập lịch hẹn trung tâm.\n2. Liệt kê dữ liệu và đối tượng liên quan.\n3. Đề xuất action cần làm trong backend, frontend, database.\n4. Kiểm tra xem action đã đáp ứng yêu cầu hay chưa.\n\nVí dụ vấn đề: bệnh nhân không nhận được email xác nhận hẹn.\n```\n''',
    '07-RAG': '''# 07-RAG\n\nMẫu prompt áp dụng trong dự án Dental Management System:\n\n```text\nDựa trên tài liệu thiết kế hệ thống Dental Management System trong thư mục docs, hãy trả lời câu hỏi sau:\n"Các module nào quản lý hồ sơ bác sĩ, bệnh nhân, lịch hẹn và thanh toán?"\nHãy trả lời bằng cách trích dẫn tên module, chức năng tương ứng và các bảng dữ liệu liên quan nếu có.\nNếu thông tin không có trong tài liệu, hãy trả lời rõ ràng rằng thông tin chưa được ghi nhận.\n```\n''',
    '08-Sinh-ma-nguon': '''# 08-Sinh-ma-nguon\n\nMẫu prompt áp dụng trong dự án Dental Management System:\n\n```text\nViết mã Python Django cho module Dental Management System quản lý bệnh nhân.\nYêu cầu: model Patient gồm họ tên, ngày sinh, giới tính, điện thoại, email, địa chỉ, bệnh sử; serializer cho API; endpoint GET/POST bệnh nhân; danh sách validation; quyền truy cập chỉ cho nhân viên quản lý.\nKết quả nên có code theo chuẩn Django REST Framework.\n```\n''',
    '09-Prompt-cho-go-loi': '''# 09-Prompt-cho-go-loi\n\nMẫu prompt áp dụng trong dự án Dental Management System:\n\n```text\nHãy kiểm tra hệ thống Dental Management System đang bị lỗi ở phần đặt lịch hẹn khi bác sĩ bận.\nLỗi có thể nằm ở: API validate lịch hẹn, serializer, model Appointment, giao diện người dùng, hoặc quy tắc cơ sở dữ liệu.\nHãy mô tả nguyên nhân, nơi phát sinh, và đề xuất sửa tối thiểu 03 cách tiếp cận để khắc phục.\n```\n''',
    '10-Prompt-cho-sinh-kien-thu': '''# 10-Prompt-cho-sinh-kien-thu\n\nMẫu prompt áp dụng trong dự án Dental Management System:\n\n```text\nBạn là trợ lý phát triển hệ thống Dental Management System.\nHãy xây dựng kịch bản thực thi tình huống: bệnh nhân đặt lịch hẹn, bác sĩ không thể nhận lịch do lịch làm việc bất khả dụng, hệ thống tự động gửi thông báo, nhân viên phòng khám gọi điện xác nhận và cập nhật trạng thái hẹn.\nNêu rõ quy trình, văn bản thông báo, bước hành động, và tiêu chí hoàn tất.\n```\n''',
    '11-Prompt-cho-viet-tai-lieu': '''# 11-Prompt-cho-viet-tai-lieu\n\nMẫu prompt áp dụng trong dự án Dental Management System:\n\n```text\nHãy viết tài liệu API cho module Appointment của Dental Management System.\nNội dung tài liệu gồm: mô tả module, endpoint POST /appointments, endpoint GET /appointments/{id}, tham số request, tham số response, trạng thái lỗi, ví dụ JSON gửi/nhận, xác thực token, và mô tả quy tắc nghiệp vụ liên quan tới hẹn khám.\n```\n''',
    '12-Prompt-cho-tac-vu-lap-trinh-nang-cao': '''# 12-Prompt-cho-tac-vu-lap-trinh-nang-cao\n\nMẫu prompt áp dụng trong dự án Dental Management System:\n\n```text\nHãy triển khai tính năng tự động gợi ý lịch hẹn tối ưu cho bác sĩ dựa trên lịch làm việc, thời lượng điều trị, loại hẹn, và mức độ ưu tiên khám của bệnh nhân.\nYêu cầu: tạo mô hình thuật toán gợi ý, lưu trữ cấu hình, API gợi ý lịch, và kiểm thử tình huống phòng khám nhiễu.\nVới mỗi bước, mô tả input, logic, output và quy tắc ràng buộc.\n```\n''',
    '13-Chu-trinh-quant-ly': '''# 13-Chu-trinh-quant-ly\n\nMẫu prompt áp dụng trong dự án Dental Management System:\n\n```text\nLập kế hoạch triển khai dự án Dental Management System theo chu trình quản lý: thăm dò yêu cầu, phân tích nghiệp vụ, thiết kế mô hình dữ liệu, thiết kế API, phát triển, kiểm thử, triển khai và bảo trì.\nHãy chia dự án thành giai đoạn 01-04 tuần, nêu sản phẩm cần hoàn thành, KPI và rủi ro ở từng giai đoạn.\n```\n''',
    '14-Kiem-thu-va-tinh-chinh': '''# 14-Kiem-thu-va-tinh-chinh\n\nMẫu prompt áp dụng trong dự án Dental Management System:\n\n```text\nHãy tạo kế hoạch kiểm thử cho Dental Management System với các module: bệnh nhân, lịch hẹn, bác sĩ, thanh toán, báo cáo.\nCác mức kiểm thử: unit test, integration test, API test, UI test, regression test.\nMỗi test case phải có: mục đích, dữ liệu đầu vào, kỳ vọng, điều kiện thành công, và điều kiện thất bại.\n```\n''',
    '15-Bao-mat-prompt': '''# 15-Bao-mat-prompt\n\nMẫu prompt áp dụng trong dự án Dental Management System:\n\n```text\nHãy đánh giá mức độ an toàn của các prompt và hệ thống AI được sử dụng trong Dental Management System.\nCần xem xét: bảo mật hồ sơ bệnh nhân, tránh tiết lộ dữ liệu cá nhân, kiểm soát quyền truy cập, log và lưu trữ, ràng buộc prompt injection, kiểm tra đầu vào đầu ra, và lưu trữ token theo chuẩn riêng tư.\nĐề xuất một checklist an toàn trước khi triển khai AI trong hệ thống.\n```\n''',
}

for folder in folders:
    folder_path = os.path.join(root, folder)
    os.makedirs(folder_path, exist_ok=True)
    with open(os.path.join(folder_path, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(contents[folder])

print(f'Created {len(folders)} prompt folders under {root}.')
