# Lát 5 — Tổng duyệt và chốt bộ hồ sơ báo cáo

## Mục tiêu và trạng thái thực tế

Tài liệu này gom tài liệu bàn giao, thứ tự trình bày, checklist chạy thử và phương án xử lý sự cố. Đây là kế hoạch sẵn sàng để nhóm cùng chốt; không ghi nhận thay cho một buổi tổng duyệt thật.

| Hạng mục | Trạng thái | Ghi chú / việc cần làm |
|---|---|---|
| Slide và tài liệu kỹ thuật | Có | Slide 13 trang; kiến trúc, ERD và hai sequence nằm trong bộ tài liệu bên dưới. |
| Kịch bản và dữ liệu demo | Có | Dùng dữ liệu synthetic, tài khoản theo role; tên người trình bày còn để trống. |
| Ứng dụng và luồng nghiệp vụ | Có để chạy thử | Chạy trên database demo riêng; xác nhận lại đăng nhập, màn hình và dữ liệu trong ngày tổng duyệt. |
| Gemini trực tiếp | Chưa sẵn sàng | Chỉ trình diễn nếu được phê duyệt, có key và consent demo; nếu không, nêu đây là tích hợp tùy chọn chưa bật. |
| Video dự phòng Lát 4 | Chưa có | Cần quay và kiểm tra video thật trước khi đánh dấu phương án dự phòng sẵn sàng. |
| Phân công thành viên | Chưa chốt | Nhóm điền tên, người giữ máy, người chuyển slide và người xử lý sự cố. |
| Tổng duyệt toàn nhóm | Chưa thực hiện | Cần chạy thử từ đầu đến cuối, bấm giờ, ghi lỗi, sửa và chạy lại. |

## Bộ hồ sơ dùng khi báo cáo

1. [Slide trình bày dự án (PPTX)](./project-presentation.pptx) — 13 trang, từ bối cảnh đến kịch bản chạy thử.
2. [Bản PDF của slide](./project-presentation.pdf) — dùng làm bản xem/in dự phòng.
3. [Kiến trúc, ERD và sequence](./architecture-and-design.md) — mô tả hệ thống hiện trạng và các điều kiện của tích hợp AI/SMS.
4. [Kịch bản demo và dữ liệu minh họa](./slice-3-demo-runbook.md) — chuẩn bị môi trường, dữ liệu synthetic, thao tác, đầu ra và xử lý lỗi.
5. [README chạy ứng dụng](../README.md) — cài đặt, khởi động backend/frontend và tài khoản demo.
6. Video dự phòng: **chưa có**; bổ sung liên kết/vị trí dùng chung sau khi hoàn thành Lát 4.

Generator PowerPoint trên Windows là `docs/generate-project-presentation.ps1`. Nếu tạo lại slide, xuất lại cả PPTX/PDF, kiểm tra đủ 13 trang và so sánh nội dung hai bản trước khi dùng.

## Kịch bản tổng duyệt đề xuất — 10 phút

Thời lượng và phân vai dưới đây là khung đề xuất, chưa phải phân công đã được nhóm xác nhận. Điền tên sau khi thống nhất.

| Thời gian | Người phụ trách | Nội dung và bàn giao |
|---|---|---|
| 00:00–01:00 | Thành viên A: __________ | Mở đầu: bài toán, mục tiêu, phạm vi và lưu ý đây là hệ thống quản lý nha khoa. |
| 01:00–02:30 | Thành viên A: __________ | Trình bày kiến trúc, ERD và nơi backend/frontend/database phối hợp. Bàn giao cho người demo. |
| 02:30–05:30 | Thành viên B: __________ | Demo lễ tân: tra cứu bệnh nhân synthetic, tiếp nhận/đặt lịch; mở bệnh án demo và chỉ rõ dữ liệu được lưu. |
| 05:30–07:00 | Thành viên C: __________ | Demo hóa đơn `DEMO-INV-001` và thanh toán tiền mặt trong database demo; cho xem trạng thái sau thanh toán. |
| 07:00–08:00 | Thành viên C: __________ | Chatbot tra cứu giá/lịch và dashboard phù hợp với role. Nêu chatbot tra cứu theo quy tắc, không phải LLM. |
| 08:00–09:15 | Thành viên A hoặc C: __________ | Nêu hai luồng Gemini/SMS là tích hợp tùy chọn. Chỉ thử Gemini trực tiếp nếu đã đủ phê duyệt, consent demo và key; reminder preview không gửi SMS. |
| 09:15–10:00 | Thành viên A: __________ | Kết luận giá trị, giới hạn, an toàn dữ liệu; mời câu hỏi. Chuyển sang video dự phòng nếu demo trực tiếp lỗi. |

Nếu nhóm quyết định giữ phân bổ 3/3/4 phút trên slide, cập nhật bảng này và lời thoại theo quyết định chung trước buổi báo cáo. Không tự thay vai trò bằng tên chưa được nhóm xác nhận.

## Checklist trước tổng duyệt

### Tài liệu và phối hợp

- [ ] Nhóm xác nhận bộ slide, thời lượng thực tế, thứ tự nói và thuật ngữ sử dụng.
- [ ] Điền tên A/B/C; chỉ định người điều khiển máy, chuyển slide, ghi thời gian và xử lý sự cố.
- [ ] Mở thử PPTX và PDF trên đúng máy trình chiếu; xác nhận font, hình ảnh, liên kết và đủ 13 trang.
- [ ] Mở tài liệu kiến trúc để có thể giải thích kiến trúc, ERD, sequence summary và reminder preview.
- [ ] Không nói Gemini/Twilio đã chạy thật nếu chưa kiểm tra tích hợp trực tiếp trên môi trường được duyệt.

### Ứng dụng và dữ liệu

- [ ] Khởi động backend/frontend theo README; xác nhận `/api/v1/health/` trả `status: ok`.
- [ ] Dùng database demo cô lập và chỉ dữ liệu synthetic; xác nhận hồ sơ, lịch, EMR, dịch vụ và hóa đơn liên kết.
- [ ] Đặt mật khẩu demo cục bộ an toàn; thử đăng nhập Admin, Lễ tân và Bác sĩ. Không ghi mật khẩu vào slide, video hoặc Git.
- [ ] Kiểm tra đăng xuất ở thanh trên cùng; trình diễn ứng dụng này như hệ thống nội bộ nhân viên, không như cổng tự đăng ký của khách hàng.
- [ ] Thử các URL trang trực tiếp và điều hướng: `/patients`, `/appointments`, `/billing`, `/emr`; kiểm tra Back/Forward.
- [ ] Dùng số điện thoại synthetic có ký tự `X`; consent AI/SMS seed mặc định false. Không thay bằng số thật, không chạy lệnh gửi SMS thật.
- [ ] Xác nhận dashboard và các số tổng hợp khớp dữ liệu hiện có; ngày trên giao diện là ngày thực tại múi giờ Việt Nam.
- [ ] Nếu Gemini chưa cấu hình, bỏ thao tác gọi thật và nói rõ là tích hợp tùy chọn chưa hoạt động trong môi trường demo.

### Bản ghi dự phòng và an toàn

- [ ] Quay video màn hình thật theo runbook Lát 3 sau khi chốt kịch bản và dữ liệu.
- [ ] Rà video để chắc chắn không lộ bệnh nhân thật, mật khẩu, token, API key, thông báo cá nhân hoặc thông tin ngoài phạm vi.
- [ ] Phát hết video từ file lưu tại thư mục chung; kiểm tra tiếng/hình, thứ tự thao tác và mở được khi ngoại tuyến.
- [ ] Ghi rõ ai bật video, vị trí file, và câu chuyển tiếp khi demo trực tiếp dừng giữa chừng.

## Checklist trong buổi tổng duyệt

- [ ] Bắt đầu bấm giờ từ lời mở đầu; ghi thời lượng thực tế từng phần và thời gian bàn giao giữa thành viên.
- [ ] Chạy liên tục các luồng theo thứ tự; không sửa trực tiếp dữ liệu production hoặc tạo giao dịch thật.
- [ ] Ghi lỗi/nội dung sai vào bảng dưới; sửa lỗi ảnh hưởng tính đúng đắn hoặc khả năng demo rồi chạy lại phần liên quan.
- [ ] Thử phương án chuyển sang video dự phòng sau một tình huống lỗi giả lập không phá dữ liệu.
- [ ] Kết thúc bằng xác nhận của cả nhóm về nội dung, phân vai, thời lượng và tệp sử dụng.

| Thời điểm / phần | Vấn đề gặp phải | Mức ảnh hưởng | Người xử lý | Đã sửa / chạy lại |
|---|---|---|---|---|
|  |  |  |  |  |
|  |  |  |  |  |

## Kịch bản sự cố và bàn giao

| Sự cố | Hành động ngay | Người phụ trách cần chốt |
|---|---|---|
| Không mở được web / API | Dừng thao tác; kiểm tra health endpoint và backend/frontend. Không seed vào database khác để chữa cháy. | Người chạy ứng dụng: __________ |
| Không đăng nhập được | Xác nhận đúng role, username và mật khẩu demo đã đặt; dùng account role khác đã được thử trước. Không đưa mật khẩu lên màn chiếu. | Người quản lý tài khoản: __________ |
| Dữ liệu trống hoặc khác kỳ vọng | Xác nhận đang dùng đúng database demo; dừng nếu nghi nhầm database. Chỉ seed lại database demo cô lập và kiểm tra thanh toán trước khi tiếp tục. | Người giữ dữ liệu demo: __________ |
| Gemini/API lỗi hoặc chưa có key | Bỏ thao tác gọi trực tiếp; giải thích điều kiện consent/cấu hình và giới hạn. Không đọc kết quả giả như phản hồi provider. | Người thuyết trình phần AI: __________ |
| Mất mạng hoặc ứng dụng dừng | Dừng demo trực tiếp, chuyển sang video đã kiểm thử nếu có; nếu chưa có video, trình bày bằng slide và thông báo rõ giới hạn. | Người điều khiển máy/video: __________ |
| Slide/file không mở | Chuyển qua PDF đã lưu cục bộ; nếu cả hai lỗi, dùng bản sao trên thiết bị dự phòng đã kiểm tra. | Người giữ tài liệu: __________ |

## Tiêu chí đóng Lát 5

Chỉ đánh dấu Lát 5 hoàn tất sau khi nhóm điền người phụ trách, xác nhận thời lượng/thứ tự, kiểm tra đủ bộ tài liệu, hoàn thành tổng duyệt từ đầu đến cuối, xử lý và chạy lại các lỗi quan trọng, đồng thời thử được phương án dự phòng. Video Lát 4 hiện chưa có và tổng duyệt nhóm chưa được ghi nhận; vì vậy Lát 5 hiện mới ở trạng thái **đã chuẩn bị hồ sơ/checklist, còn chờ nhóm thực hiện và xác nhận**.
