# 1. TỔNG QUAN DỰ ÁN

## 1.1. Bối cảnh dự án
Dự án xây dựng hệ thống quản lý nha khoa có tích hợp AI nhằm giải quyết các vấn đề thực tiễn của phòng khám nha khoa khi quản lý bệnh nhân, bác sĩ, lịch hẹn, hồ sơ điều trị, danh mục dịch vụ, hóa đơn và lịch tái khám theo ngày. Theo mô tả trong project.md, tình trạng quản lý bằng sổ sách hoặc bảng tính rời rạc dễ dẫn đến sai sót trong xếp lịch, khó tra cứu lịch sử điều trị dài hạn, mất nhiều thời gian tổng hợp doanh thu và công nợ, đồng thời làm giảm hiệu quả làm việc của nhân sự.

## 1.2. Mục tiêu chính
- Xây dựng hệ thống quản lý toàn diện cho phòng khám nha khoa trong các lĩnh vực: bệnh nhân, bác sĩ, lịch hẹn, hồ sơ điều trị răng, dịch vụ, thanh toán và tái khám.
- Tích hợp AI cho các chức năng: tóm tắt quá trình điều trị từ ghi chú lâm sàng, sinh tin nhắn nhắc lịch tái khám và giải thích dịch vụ nha khoa bằng ngôn ngữ dễ hiểu cho bệnh nhân.
- Sử dụng AI hỗ trợ trong toàn bộ vòng đời phát triển phần mềm, từ phân tích nghiệp vụ, thiết kế, sinh mã nguồn CRUD, kiểm thử cho đến biên soạn tài liệu kỹ thuật.
- Hoàn thiện sản phẩm demo có dữ liệu mẫu, phân quyền rõ ràng theo vai trò và khả năng vận hành ổn định trên môi trường local.

## 1.3. Lý do thực hiện
Hệ thống này được triển khai để nâng cao hiệu quả vận hành phòng khám, giảm sai sót nghiệp vụ, cải thiện trải nghiệm bệnh nhân và hỗ trợ chủ phòng khám trong quản lý tài chính, theo dõi lịch trình và công nợ. Ngoài ra, AI được tích hợp như một công cụ hỗ trợ cho các nhiệm vụ lặp lại và mang tính chuyên môn cao, giúp tóm tắt tiến độ điều trị và giải thích dịch vụ trong ngôn ngữ thân thiện với bệnh nhân.

## 1.4. Tiêu chí nghiệm thu dự án
- Hệ thống quản lý cốt lõi hoạt động ổn định theo các nghiệp vụ chính của phòng khám nha khoa.
- Tính năng AI được tích hợp trực tiếp vào quy trình nghiệp vụ thực tế và không thay thế vai trò chuyên môn của bác sĩ.
- Có phân quyền rõ ràng cho vai trò Quản trị viên, Bác sĩ và Lễ tân.
- Đã có dữ liệu mẫu thực tế và khả năng demo trên môi trường local.
- Tài liệu phân tích, thiết kế và hướng dẫn sử dụng đáp ứng chuẩn cần thiết cho chuỗi SDLC tiếp theo.

# 2. PHẠM VI DỰ ÁN (IN-SCOPE & OUT-OF-SCOPE)

## 2.1. In-Scope
- Quản lý thông tin bệnh nhân, lịch sử khám, tiền sử bệnh lý nha khoa.
- Quản lý thông tin bác sĩ, chuyên môn, lịch làm việc và ca trực.
- Quản lý lịch hẹn: đặt lịch, đổi lịch, hủy lịch, kiểm soát trùng khung giờ của bác sĩ.
- Quản lý hồ sơ điều trị răng: tình trạng răng, chẩn đoán, y lệnh điều trị, thủ thuật thực hiện.
- Quản lý danh mục dịch vụ nha khoa: niềng răng, nhổ răng khôn, tẩy trắng, trám răng, v.v.
- Quản lý thanh toán và hóa đơn: tổng tiền, giảm giá, phương thức thanh toán, trạng thái thanh toán.
- Quản lý lịch tái khám và nhắc nhở bệnh nhân.
- Tích hợp AI để tóm tắt điều trị, sinh tin nhắn nhắc tái khám và giải thích dịch vụ nha khoa có cảnh báo an toàn y tế.
- Phân quyền truy cập theo vai trò: Quản trị viên, Bác sĩ, Lễ tân.
- Hoạt động demo cục bộ với dữ liệu mẫu phục vụ trình bày và kiểm thử.
- Lưu trữ tài liệu kỹ thuật, prompt và nhật ký hỗ trợ AI trong dự án.

## 2.2. Out-of-Scope
- Phát triển hệ thống đa chi nhánh, kế toán tổng hợp hoặc nhân sự phức tạp vượt quá phạm vi demo phòng khám.
- Tích hợp cổng thanh toán ngân hàng/ghi nợ trực tiếp với hệ thống bên ngoài trong môi trường thực tế.
- Sử dụng AI để thay thế chẩn đoán y khoa hoặc quyết định chuyên môn của bác sĩ.
- Triển khai hệ thống lên môi trường production thực tế khi chưa có yêu cầu rõ ràng trong đầu vào.
- Viết chi tiết thiết kế lớp, ERD, schema database, API, test case trong tài liệu này; các nội dung đó sẽ được xây dựng trong các tài liệu tiếp theo trong pipeline SDLC.

# 3. NHÂN SỰ VÀ BÊN LIÊN QUAN (STAKEHOLDERS)

## 3.1. Bảng Stakeholders
| Vai trò | Thành viên | Nhiệm vụ chính |
|---|---|---|
| Trưởng nhóm | Đào Tú Uyên | Lãnh đạo kế hoạch, điều phối tiến độ, tổng hợp tài liệu và đảm bảo tiến độ chung của dự án. |
| Phó nhóm | Đỗ Thị Kim Ngân | Hỗ trợ quản lý công việc, kiểm tra tiến độ thực hiện và phối hợp tài liệu nội bộ. |
| Quản trị viên | Quản lý phòng khám | Theo dõi hoạt động, doanh thu, phân quyền và điều hành chung. |
| Bác sĩ | Bác sĩ nha khoa | Theo dõi hồ sơ bệnh nhân, ghi chú điều trị, ra y lệnh và quyết định thủ thuật. |
| Lễ tân | Nhân viên tiếp đón | Quản lý đặt lịch, cập nhật thông tin bệnh nhân, hỗ trợ công tác tiếp đón. |
| Bệnh nhân | Khách hàng của phòng khám | Đặt lịch, nhận thông tin điều trị và nhắc nhở tái khám. |
| Nhóm phát triển | Tất cả thành viên tham gia dự án | Thực hiện phân tích, thiết kế, xây dựng, kiểm thử và biên soạn tài liệu. |

## 3.2. Phân công theo vai trò
- Trưởng nhóm chịu trách nhiệm lên kế hoạch và điều phối chung.
- Phó nhóm hỗ trợ quản lý tiến độ, nội dung và phối hợp giữa các phần công việc.
- Bác sĩ đóng vai trò chủ chốt trong quản lý hồ sơ y tế và các quy trình điều trị.
- Lễ tân chịu trách nhiệm xử lý lịch hẹn và các tác vụ tiếp nhận bệnh nhân.
- Quản trị viên hỗ trợ giám sát tình hình kinh doanh và quyền truy cập hệ thống.

# 4. DANH SÁCH SẢN PHẨM BÀN GIAO (DELIVERABLES)

## 4.1. Sản phẩm bàn giao theo chuỗi SDLC
| STT | Tài liệu / Deliverable | Mục đích chính |
|---|---|---|
| 1 | 01-project-plan.md | Kế hoạch tổng quan về phạm vi, nguồn lực, rủi ro và mốc thực hiện. |
| 2 | 02-requirements-qa.md | Kiểm tra và làm rõ yêu cầu nghiệp vụ dựa trên đề tài và mục tiêu. |
| 3 | 03-requirements-specification.md | Mô tả yêu cầu chức năng và phi chức năng chính thức. |
| 4 | 04-object-oriented-design.md | Thiết kế hướng đối tượng, chức năng và kiến trúc hệ thống. |
| 5 | 05-functional-testing.md | Kịch bản kiểm thử chức năng quản lý và tích hợp AI. |
| 6 | 06-database.md | Thiết kế cơ sở dữ liệu, ràng buộc và dữ liệu mẫu. |
| 7 | 07-user-guide.md | Hướng dẫn sử dụng hệ thống cho người dùng và demo cuối kỳ. |

## 4.2. Sản phẩm hỗ trợ trong dự án
- Thư mục docs/KN1 lưu trữ toàn bộ hồ sơ dự án.
- Thư mục genai lưu báo cáo tương tác với AI, prompt và nhật ký đóng góp hỗ trợ phát triển.
- Thư mục diagrams lưu sơ đồ nghiệp vụ, sơ đồ use case, sơ đồ kiến trúc hoặc ERD nếu cần.

# 5. KẾ HOẠCH MỐC THỜI GIAN (MILESTONES)

## 5.1. Đề xuất lịch trình thực hiện
| Giai đoạn | Mốc | Nội dung chính |
|---|---|---|
| Giai đoạn 1 | Khởi tạo và phân tích ban đầu | Xác định bối cảnh, phạm vi, stakeholder và yêu cầu trọng tâm. |
| Giai đoạn 2 | Hoàn thiện yêu cầu | Làm rõ yêu cầu nghiệp vụ và phân chia phạm vi cho từng vai trò. |
| Giai đoạn 3 | Thiết kế hệ thống | Định nghĩa kiến trúc, luồng nghiệp vụ và dữ liệu cần quản lý. |
| Giai đoạn 4 | Phát triển chức năng quản lý | Xây dựng CRUD cho bệnh nhân, bác sĩ, lịch hẹn, dịch vụ, thanh toán và tái khám. |
| Giai đoạn 5 | Tích hợp AI | Hoàn thiện prompt, đầu vào/đầu ra AI và kiểm soát cảnh báo y tế. |
| Giai đoạn 6 | Kiểm thử | Đánh giá chức năng quản lý và tích hợp AI theo kịch bản phù hợp. |
| Giai đoạn 7 | Bàn giao và demo | Hoàn thiện tài liệu, hướng dẫn sử dụng và trình bày sản phẩm. |

## 5.2. Ghi chú về thời gian
Thông tin đầu vào không nêu mốc thời gian cụ thể hoặc deadline chính thức. Vì vậy, kế hoạch trên là lịch trình tham khảo để nhóm thực hiện theo tiến độ SDLC. Nếu có mốc thời gian giảng viên hoặc lịch học cụ thể, cần được xác nhận bổ sung.

# 6. QUẢN LÝ RỦI RO (RISK MANAGEMENT)

| Loại rủi ro | Mô tả rủi ro | Mức độ | Giải pháp giảm thiểu |
|---|---|---|---|
| Nghiệp vụ | Quy trình khám chữa, đặt lịch và tái khám chưa được làm rõ hoàn toàn | Trung bình | Xác định rõ quy trình từ đề tài và cập nhật bổ sung nếu cần giữa các thành viên. |
| Nhân sự | Phân công công việc chưa đồng đều, nhóm chưa xác định rõ vai trò và trách nhiệm | Trung bình | Phân công theo vai trò, theo dõi tiến độ và hỗ trợ lẫn nhau. |
| Kỹ thuật | Chưa thống nhất công nghệ backend, frontend và AI engine | Cao | Chốt stack phù hợp ngay từ đầu và giữ nền tảng demo khả thi, rõ ràng. |
| Dữ liệu | Thông tin bệnh nhân, lịch hẹn và thanh toán dễ sai lệch nếu không có ràng buộc | Cao | Xác định dữ liệu đầu vào, chuẩn hóa mô hình dữ liệu và kiểm thử dữ liệu mẫu. |
| AI | AI có thể sinh nội dung không phù hợp hoặc vượt phạm vi y tế | Cao | Ràng buộc prompt, cảnh báo y tế, kiểm soát đầu vào và định dạng đầu ra. |
| Bảo mật | Lộ API key hoặc dữ liệu nhạy cảm của bệnh nhân | Cao | Đặt thông tin nhạy cảm trong file .env, không lưu dữ liệu nhạy cảm trong repo. |
| Thời gian | Dự án có nhiều chức năng nhưng thời lượng thực hiện có hạn | Trung bình | Chia theo giai đoạn SDLC, ưu tiên chức năng cốt lõi và tài liệu bàn giao. |

# 7. VẤN ĐỀ CẦN XÁC MINH & GIẢ ĐỊNH

## 7.1. Vấn đề cần xác minh
- Công nghệ backend cụ thể nào sẽ được chọn: FastAPI, Flask hay Django?
- Frontend sẽ sử dụng React, Vue hoặc HTML/CSS/JavaScript thuần?
- CSDL demo sẽ là SQLite, MySQL hay PostgreSQL?
- AI engine sẽ dùng OpenAI, Gemini, Claude, Hugging Face hay Ollama?
- Cấu trúc lưu trữ prompt và nhật ký AI có cần thêm thư mục riêng ngoài yêu cầu hiện có không?
- Có cần thêm vai trò nào ngoài Quản trị viên, Bác sĩ và Lễ tân hay không?

## 7.2. Giả định cần xác nhận
- Dự án được triển khai như một sản phẩm demo cục bộ, không yêu cầu môi trường production ngay từ đầu.
- AI được xem như công cụ hỗ trợ nghiệp vụ và cảnh báo an toàn y tế, không thay thế chẩn đoán của bác sĩ.
- Toàn bộ thành viên nhóm tham gia vào các giai đoạn phân tích, thiết kế, phát triển và kiểm thử.
- Tài liệu sẽ được lưu trong thư mục docs/KN1 và các thư mục con tương ứng như genai, diagrams.

## 7.3. Kết luận ban đầu
Dự án có phạm vi rõ ràng, tập trung vào hệ thống quản lý phòng khám nha khoa có tích hợp AI. Mục tiêu chính là xây dựng một sản phẩm demo có tính thực tiễn, phân quyền rõ ràng, kết nối được nghiệp vụ quản lý và AI để hỗ trợ người dùng, đồng thời đủ tiêu chuẩn tài liệu để thực hiện tiếp các giai đoạn phát triển trong chuỗi SDLC. Tuy nhiên, vì thông tin đầu vào chưa xác định đầy đủ về công nghệ và thời gian cụ thể, các quyết định kỹ thuật cần được xác nhận bổ sung trong quá trình thực hiện tiếp theo.

## 7.4. Tiêu chuẩn nghiệm thu tổng thể
- Các chức năng quản lý cốt lõi của phòng khám nha khoa phải hoạt động đầy đủ và ổn định.
- AI phải tích hợp trực tiếp vào quy trình nghiệp vụ, không tách biệt khỏi sản phẩm.
- Phân quyền theo vai trò phải rõ ràng và hiệu quả.
- Tài liệu, prompt và dữ liệu demo phải đủ để phục vụ tư duy thiết kế và kiểm thử.
- Thực hiện đúng nguyên tắc quản lý dự án PMBOK/Agile và bám sát thông tin đầu vào từ project.md và informember.md.
