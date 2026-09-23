Hệ thống quản lý nha khoa có tích hợp AI
1. Mô tả bài toán
Các phòng khám nha khoa cần quản lý thông tin bệnh nhân, bác sĩ, lịch hẹn, hồ sơ điều trị răng, danh mục dịch vụ, thanh toán và lịch tái khám hằng ngày. Nếu quản lý bằng sổ sách hoặc bảng tính rời rạc, nhân viên dễ gặp sai sót khi xếp lịch, khó tra cứu lịch sử điều trị dài hạn của bệnh nhân và mất nhiều thời gian tổng hợp doanh thu, theo dõi công nợ. Đề tài yêu cầu xây dựng hệ thống quản lý nha khoa giúp nhân viên lễ tân thao tác nhanh, bác sĩ theo dõi hồ sơ điều trị chính xác, chủ phòng khám quản lý tài chính hiệu quả, đồng thời sử dụng AI để hỗ trợ tóm tắt quá trình điều trị từ ghi chú của bác sĩ, sinh tin nhắn nhắc lịch tái khám và giải thích dịch vụ nha khoa bằng ngôn ngữ dễ hiểu cho bệnh nhân.

2. Mục tiêu
Xây dựng hệ thống quản lý toàn diện các thực thể: bệnh nhân, bác sĩ, lịch hẹn, hồ sơ điều trị răng, dịch vụ, thanh toán và lịch tái khám.

Tích hợp AI tạo sinh để hỗ trợ tóm tắt quá trình điều trị từ ghi chú lâm sàng, tự động sinh tin nhắn nhắc lịch tái khám và giải thích dịch vụ nha khoa dưới dạng tham khảo kèm cảnh báo y tế.

Sử dụng AI trong vòng đời phát triển phần mềm (SDLC) để phân tích nghiệp vụ nha khoa, thiết kế cơ sở dữ liệu, sinh mã nguồn CRUD, kiểm thử và biên soạn tài liệu kỹ thuật.

Hoàn thiện sản phẩm có dữ liệu mẫu thực tế, phân quyền chặt chẽ theo vai trò (Quản trị viên, Bác sĩ, Lễ tân) và có khả năng demo ổn định trên môi trường local.

3. Yêu cầu chức năng
3.1. Chức năng quản lý
Đăng nhập, đăng xuất và phân quyền chi tiết cho Quản trị viên, Bác sĩ và Lễ tân.

Quản lý bệnh nhân: thông tin cá nhân, tiền sử bệnh lý nha khoa, lịch sử khám chữa bệnh.

Quản lý bác sĩ: thông tin chuyên môn, lịch làm việc, ca trực tại phòng khám.

Quản lý lịch hẹn: đặt lịch, đổi lịch, hủy lịch khám, tránh trùng lặp khung giờ của bác sĩ.

Quản lý hồ sơ điều trị răng: ghi nhận tình trạng răng hàm mặt, chẩn đoán, y lệnh điều trị của bác sĩ và các thủ thuật thực hiện.

Quản lý dịch vụ nha khoa: danh mục dịch vụ (niềng răng, nhổ răng khôn, tẩy trắng, trám răng...), đơn giá và mô tả chi tiết.

Quản lý thanh toán và hóa đơn: tính tổng tiền dịch vụ, giảm giá, ghi nhận phương thức thanh toán (tiền mặt, chuyển khoản, thẻ) và trạng thái thanh toán.

Quản lý lịch tái khám: theo dõi mốc thời gian bệnh nhân cần quay lại kiểm tra định kỳ.

3.2. Chức năng AI
Tóm tắt quá trình điều trị: nhận đầu vào là các ghi chú lâm sàng dài của bác sĩ sau nhiều buổi khám và sinh ra bản tóm tắt ngắn gọn, mạch lạc về tiến trình điều trị.

Sinh tin nhắn nhắc lịch tái khám: tự động tạo nội dung tin nhắn SMS/Zalo cá nhân hóa nhắc nhở bệnh nhân lịch hẹn tái khám sắp tới dựa trên dữ liệu lịch hẹn.

Giải thích dịch vụ nha khoa: chuyển đổi các thuật ngữ y khoa phức tạp thành ngôn ngữ phổ thông, dễ hiểu để giải thích cho bệnh nhân ở mức độ tham khảo, bắt buộc đi kèm cảnh báo rõ ràng không thay thế chẩn đoán của bác sĩ.

4. Yêu cầu kỹ thuật
Backend: Python (FastAPI / Flask / Django).

Frontend: React, Vue, hoặc HTML/CSS/JavaScript.

Cơ sở dữ liệu: SQLite cho bản demo cục bộ; hỗ trợ MySQL hoặc PostgreSQL.

AI Engine: OpenAI API, Gemini API, Claude API, Hugging Face hoặc Ollama.

Cấu trúc mã nguồn: Prompt template tách riêng trong thư mục prompts/.

Cấu hình bảo mật: API key đặt trong tệp .env, đi kèm tệp mẫu .env.example.

Kiểm thử: Có bộ test case tự động cho lịch hẹn, hồ sơ điều trị, thanh toán và các tính năng tích hợp AI.

5. Dữ liệu đầu vào, đầu ra và dữ liệu hệ thống
Dữ liệu chính: người dùng, vai trò, bệnh nhân, bác sĩ, lịch hẹn, hồ sơ điều trị, danh mục dịch vụ, hóa đơn chi tiết, lịch tái khám.

Đầu vào quản lý: biểu mẫu thông tin bệnh nhân, lịch hẹn, y lệnh điều trị, hóa đơn thanh toán, bộ lọc thời gian và bác sĩ.

Đầu vào AI: ghi chú khám bệnh của bác sĩ, thông tin lịch hẹn tái khám, câu hỏi hoặc yêu cầu giải thích dịch vụ từ người dùng.

Đầu ra quản lý: giao diện bảng dữ liệu (grid), hóa đơn nha khoa, bảng điều khiển (dashboard) thống kê doanh thu và lịch trình.

Đầu ra AI: đoạn văn bản tóm tắt điều trị, nội dung tin nhắn nhắc lịch, văn bản giải thích dịch vụ kèm cảnh báo y tế.

Ví dụ dữ liệu mẫu:

Bệnh nhân: Nguyễn Văn A, SĐT: 0988xxxxxx, Tiền sử: Dị ứng penicillin.

Ghi chú khám của bác sĩ: "Bệnh nhân đến khám đau buốt răng số 46. Kiểm tra thấy sâu ngà sâu, đã tiến hành gây tê tủy, lấy tủy cấp cứu và hàn tạm bằng cavit. Hẹn 3 ngày sau tái khám kiểm tra."

Prompt mẫu cho chức năng AI giải thích dịch vụ:

Plaintext
System: Bạn là trợ lý AI y khoa hỗ trợ phòng khám nha khoa. Chỉ giải thích dịch vụ dựa trên thông tin dịch vụ được cung cấp. Bắt buộc phải thêm cảnh báo rằng đây chỉ là thông tin tham khảo và không thay thế chẩn đoán của bác sĩ chuyên khoa.
User: Hãy giải thích dịch vụ "Niềng răng mắc cài kim loại" bằng ngôn ngữ dễ hiểu cho bệnh nhân.
Lưu ý bảo mật: Khi gọi các dịch vụ AI, tuyệt đối ẩn hoặc không gửi các thông tin định danh cá nhân nhạy cảm của bệnh nhân (như số căn cước, thông tin thẻ tín dụng) nếu không thực sự cần thiết cho nghiệp vụ xử lý của mô hình.

6. Hướng dẫn sử dụng AI trong từng giai đoạn SDLC
Giai đoạn 1: Phân tích yêu cầu và thiết kế hệ thống (Bài KT1)
Dùng AI phân tích quy trình nghiệp vụ tiếp đón bệnh nhân, khám chữa răng, lập lịch hẹn và thanh toán viện phí.

Dùng AI hỗ trợ xác định các actor (Lễ tân, Bác sĩ, Quản trị viên, Bệnh nhân), use case chi tiết, yêu cầu chức năng và phi chức năng.

Dùng AI đề xuất cấu trúc thực thể và quan hệ cho sơ đồ ERD (Bệnh nhân, Bác sĩ, Lịch hẹn, Hồ sơ điều trị, Dịch vụ, Thanh toán).

Dùng AI gợi ý chính xác vị trí tích hợp các tính năng AI (tóm tắt ghi chú điều trị, sinh tin nhắn nhắc tái khám, giải thích dịch vụ).

Dùng AI hỗ trợ phác thảo giao diện wireframe cho màn hình tiếp nhận bệnh nhân, đặt lịch hẹn và quản lý hồ sơ điều trị.

Giai đoạn 2: Xây dựng chức năng quản lý (Bài KT2)
Dùng AI hỗ trợ sinh khung cấu trúc dự án, các model dữ liệu, schema, API CRUD cho quản lý bệnh nhân, bác sĩ và lịch hẹn.

Dùng AI viết các câu lệnh truy vấn phức tạp để thống kê lịch hẹn theo ngày, doanh thu theo dịch vụ và kiểm tra trùng lịch trực của bác sĩ.

Dùng AI hỗ trợ debug các lỗi logic liên quan đến cập nhật trạng thái lịch hẹn hoặc xung đột thời gian khám.

Lưu trữ toàn bộ nhật ký prompt và phản hồi của AI làm minh chứng trong thư mục tài liệu dự án.

Giai đoạn 3: Tích hợp AI, tối ưu prompt và kiểm thử (Bài KT3)
Dùng AI thiết kế và tinh chỉnh các prompt template cho chức năng tóm tắt điều trị và sinh tin nhắn nhắc lịch.

Dùng AI sinh mã nguồn gọi API tích hợp mô hình ngôn ngữ, xử lý các ngoại lệ như timeout, giới hạn tần suất gọi (rate limit) hoặc phản hồi sai định dạng JSON.

Dùng AI xây dựng bộ test case kiểm thử chức năng cho lịch hẹn, hồ sơ điều trị, thanh toán và các tính năng AI.

Thực hiện so sánh ít nhất 3 phiên bản prompt khác nhau để giảm thiểu tình trạng AI sinh nội dung sai lệch hoặc vượt quá phạm vi y tế cho phép.

Giai đoạn 4: Hoàn thiện, triển khai và báo cáo (Bài thi cuối kỳ)
Dùng AI hỗ trợ soạn thảo tệp README hướng dẫn cài đặt, thiết lập biến môi trường và chạy kịch bản dữ liệu mẫu cho hệ thống quản lý nha khoa.

Dùng AI kiểm tra mã nguồn (code review), rà soát các lỗ hổng bảo mật liên quan đến lộ API key hoặc phân quyền dữ liệu người dùng.

Dùng AI hỗ trợ phác thảo nội dung slide thuyết trình làm nổi bật hai vai trò cốt lõi của AI trong dự án (hỗ trợ nghiệp vụ vận dụng bên trong và hỗ trợ kỹ thuật trong SDLC).

Dùng AI hướng dẫn các bước đóng gói ứng dụng hoặc triển khai bản demo lên môi trường cloud.

7. Mức độ khó
Mức độ trung bình: Hệ thống bao gồm nhiều thực thể nghiệp vụ y tế phổ biến, đòi hỏi sự chính xác cao trong việc quản lý lịch hẹn, ràng buộc thời gian bác sĩ và hồ sơ điều trị răng miệng. Các tính năng AI tập trung vào xử lý văn bản, tóm tắt dữ liệu lâm sàng và trợ giúp quản trị dựa trên cơ sở dữ liệu sẵn có, đảm bảo kiểm soát chặt chẽ đầu vào và cơ chế cảnh báo an toàn y tế.

Hướng dẫn chấm theo tiêu chí
Tiêu chí chấm bài kiểm tra số 1 (Tuần 4 phải nộp)
Hoàn thiện chức năng hệ thống: Các chức năng quản lý cốt lõi và tích hợp AI hoạt động đầy đủ, ổn định, đúng đặc tả đề bài. (1 điểm)

Tích hợp được chức năng AI vào hệ thống: Chức năng AI được nhúng trực tiếp vào luồng nghiệp vụ phòng khám (như tóm tắt hồ sơ, nhắc lịch), không bị tách rời khỏi sản phẩm. (1 điểm)

Phân tích đúng bài toán quản lý: Xác định rõ bối cảnh đặc thù của phòng khám nha khoa, người dùng, cấu trúc dữ liệu và quy trình khám chữa bệnh. (1 điểm)

Cấu trúc dự án hợp lý: Mã nguồn được phân chia rành mạch theo các thư mục backend, frontend, database, prompts, docs đúng chuẩn framework. (1 điểm)

Chất lượng kiến trúc và mã nguồn: Code sáng sủa, phân tầng rõ ràng, dễ bảo trì và tuân thủ quy chuẩn của ngôn ngữ lập trình. (1 điểm)

Kết nối API/model AI đúng cách: Tích hợp thành công mô hình (OpenAI/Gemini/Claude/Hugging Face/Ollama) và bảo mật tuyệt đối API key. (1 điểm)

Xác định đầy đủ yêu cầu chức năng: Liệt kê chi tiết các chức năng quản lý nha khoa kèm theo đầu vào, luồng xử lý và đầu ra tường minh. (1 điểm)

Xây dựng chức năng đăng nhập và phân quyền: Thiết lập cơ chế xác thực người dùng, phân tách rõ vai trò Quản trị viên, Bác sĩ và Lễ tân. (1 điểm)

Chất lượng cơ sở dữ liệu: Thiết kế CSDL logic, tính nhất quán cao, có ràng buộc toàn vẹn, đi kèm dữ liệu mẫu và khả năng khôi phục. (1 điểm)

Thiết kế prompt có hệ thống: Tách biệt tệp prompt khỏi mã nguồn, cấu trúc rõ system/user prompt, có ràng buộc định dạng đầu ra. (1 điểm)

Tiêu chí chấm bài kiểm tra số 2 (Tuần 6 phải nộp)
Xác định yêu cầu phi chức năng: Làm rõ các tiêu chí về bảo mật dữ liệu y tế bệnh nhân, hiệu năng, khả dụng và phân quyền truy cập. (1 điểm)

Hoàn thiện CRUD nghiệp vụ chính: Các thao tác thêm, xem, sửa, xóa trên bệnh nhân, bác sĩ, dịch vụ và lịch hẹn hoạt động trơn tru. (1 điểm)

Chất lượng giao diện và trải nghiệm người dùng: Giao diện trực quan, đồng bộ, tương thích tốt trên các kích thước màn hình, xử lý phản hồi thao tác mượt mà. (1 điểm)

Tối ưu prompt qua thử nghiệm: Thực hiện tối thiểu 3 vòng thử nghiệm hoặc đối chiếu các phiên bản prompt/mô hình khác nhau, có ghi nhận kết quả cải tiến. (1 điểm)

Thiết kế actor và use case: Xác định chính xác các tác nhân (Lễ tân, Bác sĩ, Quản trị viên) và sơ đồ Use Case tương ứng cho toàn hệ thống. (1 điểm)

Xây dựng chức năng tìm kiếm và lọc: Hỗ trợ tìm kiếm, lọc và sắp xếp linh hoạt danh sách bệnh nhân, lịch hẹn và hóa đơn theo thời gian, trạng thái. (1 điểm)

Chất lượng chức năng AI: Kết quả phản hồi từ AI mang tính thực tiễn cao, bám sát ngữ cảnh nha khoa, có cơ chế giới hạn và cảnh báo y tế rõ ràng. (1 điểm)

Sử dụng dữ liệu hệ thống trong chức năng AI: Khai thác hiệu quả dữ liệu từ CSDL (như ghi chú của bác sĩ, danh mục dịch vụ) khi gọi AI và kiểm soát quyền truy cập. (1 điểm)

Thiết kế cơ sở dữ liệu: Hoàn thiện sơ đồ ERD, định nghĩa tường minh khóa chính, khóa ngoại, các ràng buộc quan hệ giữa các bảng. (1 điểm)

Xây dựng thống kê/báo cáo cơ bản: Cung cấp dashboard hoặc báo cáo doanh thu, thống kê lịch hẹn phục vụ công tác quản trị phòng khám. (1 điểm)

Tiêu chí chấm bài kiểm tra số 3 (Tuần 8 phải nộp)
Bảo mật, quyền riêng tư và đạo đức AI: Bảo vệ tài khoản người dùng, phân quyền chặt chẽ, bảo mật tuyệt đối API key và che giấu dữ liệu nhạy cảm khi gọi AI. (1 điểm)

Hiển thị kết quả AI rõ ràng: Trình bày kết quả do AI sinh ra trực quan, dễ đọc, bố cục hợp lý kèm theo các lưu ý/cảnh báo y tế cần thiết. (1 điểm)

Thiết kế kiến trúc hệ thống: Mô tả mạch lạc kiến trúc tổng thể gồm frontend, backend, database, dịch vụ AI và luồng trao đổi dữ liệu. (1 điểm)

Thiết kế giao diện rõ ràng, dễ sử dụng: Giao diện thân thiện với nhân viên y tế và lễ tân, thông báo lỗi minh bạch, phản hồi thao tác kịp thời. (1 điểm)

Hiệu năng và độ ổn định: Ứng dụng phản hồi nhanh chóng với tập dữ liệu demo, xử lý tốt các tình huống lặp hoặc lỗi phát sinh từ AI. (1 điểm)

Xử lý lỗi và giới hạn AI: Xử lý triệt để các trường hợp quá thời gian (timeout), giới hạn tần suất (rate limit), phản hồi rỗng hoặc sai cấu trúc từ mô hình. (1 điểm)

Xác định vị trí ứng dụng AI: Lựa chọn đúng đắn các điểm chạm tích hợp AI giải quyết đúng nhu cầu thực tế của phòng khám nha khoa. (1 điểm)

Kết nối và thao tác CSDL ổn định: Đảm bảo tính toàn vẹn khi đọc, ghi, cập nhật dữ liệu phòng khám; có sẵn tập dữ liệu mẫu phục vụ trình bày. (1 điểm)

Triển khai và đóng gói: Cung cấp tài liệu hướng dẫn cấu hình môi trường, chạy ứng dụng rõ ràng; khuyến khích đóng gói bằng Docker. (1 điểm)

Kiểm thử chức năng quản lý và chức năng AI: Xây dựng đầy đủ kịch bản kiểm thử (test case) cho các trường hợp hợp lệ, ngoại lệ và giá trị biên. (1 điểm)

Tiêu chí chấm Thi hết môn (kết thúc 9 tuần phải nộp)
Thiết kế prompt và luồng gọi AI sơ bộ: Xây dựng hoàn chỉnh system prompt, các mẫu user prompt, quy định định dạng đầu vào/đầu ra và các ràng buộc an toàn. (1 điểm)

Xử lý lỗi cơ bản: Xây dựng cơ chế chống sập ứng dụng (crash) khi người dùng nhập sai dữ liệu, thiếu thông tin hoặc phát sinh lỗi truy vấn cơ sở dữ liệu. (1 điểm)

Báo cáo kỹ thuật đầy đủ: Trình bày báo cáo chi tiết về quá trình phân tích, thiết kế, triển khai, kiểm thử hệ thống và vai trò hỗ trợ của AI trong chuỗi SDLC. (1 điểm)

Review code và cải thiện chất lượng bằng AI: Cung cấp minh chứng cụ thể về việc sử dụng AI để rà soát mã nguồn, phát hiện lỗ hổng và tối ưu hóa hệ thống. (1 điểm)

Minh chứng sử dụng AI trong phân tích và thiết kế: Lưu trữ đầy đủ nhật ký prompt, phản hồi từ AI và đánh giá của nhóm về việc kiểm chứng, chỉnh sửa kết quả. (1 điểm)

Minh chứng sử dụng AI khi lập trình: Cung cấp nhật ký prompt lập trình, phần code có sự hỗ trợ của AI và phần mã nguồn do nhóm tự kiểm tra, hoàn thiện. (1 điểm)

Thuyết trình và demo: Trình bày mạch lạc, tự tin demo trọn vẹn các chức năng quản lý nha khoa, tính năng AI và trả lời tốt các câu hỏi phản biện. (1 điểm)

Tích hợp chức năng AI với trải nghiệm người dùng: Đưa AI vào hệ thống một cách tự nhiên, hữu ích, không gây rối mắt hoặc nhầm lẫn với các thao tác quản lý nghiệp vụ thuần túy. (1 điểm)

Tài liệu phân tích thiết kế: Xây dựng tài liệu chuẩn mực, cấu trúc khoa học, có định hướng phát triển các giai đoạn tiếp theo của phần mềm. (1 điểm)

Quản lý mã nguồn và tài liệu chạy thử: Tệp README chuẩn chỉnh, hướng dẫn cài đặt chi tiết, có tệp .env.example và lịch sử commit rõ ràng trên hệ thống quản lý mã nguồn. (1 điểm)