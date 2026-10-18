# Lát 3 — Kịch bản demo và dữ liệu minh họa

## Phạm vi và an toàn dữ liệu

- Chỉ dùng database development/demo và dữ liệu synthetic do `python manage.py seed_dental_data` tạo. Không chạy lệnh seed trên database phòng khám hoặc database có dữ liệu cần giữ.
- Seed tạo sẵn tài khoản `admin`, `doctor1`, `doctor2`, `receptionist1`; bệnh nhân `DMS-0001`–`DMS-0005`; dịch vụ cơ bản; một lịch tương lai; một lượt khám synthetic đã hoàn tất có EMR/ngày tái khám; và hóa đơn `DEMO-INV-001` đang `ISSUED`. Điện thoại dùng sentinel không hợp lệ `0000000000`, không phải số nhận SMS.
- Consent AI và SMS mặc định **false**. Chỉ trên bệnh nhân synthetic, người phụ trách có thể ghi nhận consent demo riêng trước khi minh họa các luồng AI. Không dùng thao tác này để giả consent của bệnh nhân thật.
- Số sentinel `0000000000` không vượt qua kiểm tra định dạng di động Việt Nam trong sender Twilio; tuyệt đối không thay bằng số thật trong database seed.
- Summary gửi nội dung lâm sàng synthetic đã qua bước lọc định danh tới Gemini. Chỉ chạy khi đã được phê duyệt dùng provider và cấu hình API key cục bộ.
- Reminder preview gửi prompt chung không chứa tên, số điện thoại, ID bệnh nhân hay nội dung EMR tới Gemini. Preview chỉ hiển thị, không gửi SMS.
- Không chạy `send_follow_up_reminders` không có `--dry-run` trong demo. Lệnh gửi thật có thể liên hệ nhiều bệnh nhân đã consent và phát sinh phí Twilio.
- Không ghi mật khẩu, khóa Gemini/Twilio, JWT hoặc dữ liệu thật trong tài liệu, terminal được chia sẻ, ảnh/video hay Git.

## Chuẩn bị môi trường

Tạo đường dẫn database SQLite demo mới, không dùng database phòng khám hay database development đang có dữ liệu cần giữ. Chạy từ thư mục `backend`:

```powershell
$demoDb = Join-Path $PWD "slice3-demo.sqlite3"
if (Test-Path $demoDb) { throw "Choose a new isolated demo database path." }
$env:DMS_DB_NAME = $demoDb
python manage.py migrate
python manage.py seed_dental_data
```

Nếu cần tạo cùng mật khẩu local cho tài khoản demo, đặt `DMS_SEED_DEMO_PASSWORD` an toàn trong phiên PowerShell trước khi seed; hoặc đặt mật khẩu riêng bằng lệnh `python manage.py changepassword admin`, `doctor1`, `doctor2`, `receptionist1`. Seed không gán mật khẩu mặc định.

Khởi chạy backend và frontend theo README. Xác nhận `/api/v1/health/` trả `status: ok`, đăng nhập lần lượt với ba role, kiểm tra menu đúng role và chỉ dùng profile/database demo.

Để trình diễn Gemini thật, cấu hình `DMS_GEMINI_API_KEY` và `DMS_GEMINI_MODEL` trong môi trường cục bộ sau khi phê duyệt điều khoản dữ liệu. Khi chưa cấu hình, bỏ qua thao tác gọi provider và trình bày màn hình chặn cấu hình; không tuyên bố đã gọi AI thật.

## Phân vai và thời lượng gợi ý — 10 phút

Tên thành viên chưa được nhóm cung cấp; điền tên vào chỗ trống sau khi thống nhất. Thời lượng là kịch bản gợi ý, chưa phải buổi tổng duyệt đã diễn ra.

| Thời gian | Người phụ trách | Vai trò đăng nhập | Nội dung / bàn giao |
|---|---|---|---|
| 00:00–01:00 | Thành viên A: __________ | Admin | Nêu bài toán, phạm vi và thứ tự demo; bàn giao lễ tân. |
| 01:00–03:00 | Thành viên B: __________ | Lễ tân | Tra cứu bệnh nhân, tiếp nhận và đặt một lịch ở khung giờ trống. |
| 03:00–05:00 | Thành viên C: __________ | Bác sĩ | Mở hồ sơ khám synthetic, cập nhật EMR/ngày tái khám; gọi Gemini summary nếu đủ điều kiện. |
| 05:00–06:30 | Thành viên B: __________ | Lễ tân | Xem trước lời nhắc Gemini; nhấn mạnh đây là preview, không gửi tin. |
| 06:30–08:00 | Thành viên B: __________ | Lễ tân | Mở hóa đơn `DEMO-INV-001`, xác nhận thanh toán tiền mặt demo. |
| 08:00–09:00 | Thành viên C: __________ | Bác sĩ hoặc Lễ tân | Hỏi chatbot về giá dịch vụ/khung giờ và nêu chatbot dựa trên luật + dữ liệu ứng dụng, không dùng LLM. |
| 09:00–10:00 | Thành viên A: __________ | Admin | Mở dashboard, chọn khoảng thời gian có dữ liệu, kết luận và mời hỏi đáp. |

## Các bước demo chi tiết

| Bước | Đầu vào | Thao tác | Kết quả mong đợi | Nếu lỗi |
|---|---|---|---|---|
| 1. Health check và đăng nhập | Backend/frontend chạy; tài khoản demo đã đặt mật khẩu | Mở `/api/v1/health/`; đăng nhập Admin, Lễ tân, Bác sĩ theo thứ tự phân vai. | Health check OK; role hiển thị đúng và menu theo role. | Kiểm tra backend, Vite proxy, migrations và mật khẩu; không dùng tài khoản/dữ liệu production làm phương án thay thế. |
| 2. Tra cứu và tiếp nhận | Bệnh nhân synthetic `DMS-0001` | Lễ tân mở Reception/Patients, tìm theo mã, xác nhận thông tin demo. | Hồ sơ đúng mã synthetic được hiển thị; không tiết lộ hoặc nhập dữ liệu bệnh nhân thật. | Tìm bằng patient code; nếu thiếu dữ liệu, chạy seed lại chỉ trên database demo. |
| 3. Đặt lịch | `DMS-0001`, bác sĩ `doctor1`, dịch vụ Cleaning, ngày/khung trống trên lịch seed | Lễ tân mở Appointments và tạo lịch ở giờ còn trống trong ca; thêm ghi chú “Demo booking”. | API chấp nhận lịch trong ca, không trùng; lịch mới xuất hiện trong lịch hẹn. | Chọn giờ khác trong ca hiển thị; không sửa database trực tiếp trong lúc demo. |
| 4. Cập nhật EMR | Lịch hoàn tất synthetic của `DMS-0001`, chẩn đoán và kế hoạch minh họa trong hồ sơ seed | Bác sĩ mở EMR, xác nhận/cập nhật nội dung giả lập, dịch vụ/răng và ngày tái khám. Lưu hồ sơ. | EMR gắn đúng lịch; nội dung và ngày tái khám được lưu. | Xác nhận đăng nhập `doctor1` và lịch thuộc bác sĩ đó; dùng hồ sơ hoàn tất đã seed. |
| 5. AI tóm tắt EMR | Hồ sơ synthetic đã lưu; AI consent demo được ghi nhận riêng; Gemini đã được phê duyệt/cấu hình | Bác sĩ chọn tạo summary; đọc kết quả như bản nháp. | Gemini trả summary; hồ sơ gốc không bị ghi đè. Nếu chưa có credential, API báo chưa cấu hình và bước này được trình bày là chưa chạy thật. | Không lặp gọi liên tục; kiểm tra consent/config/rate limit. Không dán hồ sơ thật vào chatbot hay Gemini ngoài luồng được phê duyệt. |
| 6. Preview nhắc tái khám | Bệnh nhân synthetic có ngày tái khám và SMS consent demo đã ghi nhận; Gemini được cấu hình | Lễ tân mở Reminders, chọn bệnh nhân, bấm Generate reminder preview. | Hiển thị ngày hẹn và câu nhắc chung từ Gemini, nhãn “Preview only · not sent”. Prompt không có tên/số điện thoại/EMR; Twilio không được gọi. | Kiểm tra ngày tái khám, SMS consent và Gemini config. Nếu thiếu, không bật consent giả trên dữ liệu thật và bỏ qua bước AI trực tiếp. |
| 7. Hóa đơn và thanh toán | Hóa đơn synthetic `DEMO-INV-001`, `ISSUED`, giá dịch vụ Cleaning | Lễ tân mở Billing, xác nhận đúng tổng tiền demo rồi dùng xác nhận tiền mặt. | Tạo giao dịch demo `COMPLETED`, hóa đơn chuyển `PAID`, không thanh toán lặp. Không dùng tài khoản ngân hàng thật. | Dùng hóa đơn demo `ISSUED`; nếu đã thanh toán do buổi thử trước, seed lại database demo hoặc dùng dữ liệu test cô lập. |
| 8. Chatbot | Câu hỏi “Giá dịch vụ Cleaning là bao nhiêu?” hoặc câu hỏi khung giờ theo ngày | Mở chatbot và gửi câu hỏi. | Trả giá dịch vụ/giờ từ dữ liệu hiện có; không chẩn đoán, không đọc EMR và không gọi LLM. | Dùng câu hỏi đúng phạm vi giá/khung giờ; kiểm tra dịch vụ đang active và lịch seed. |
| 9. Dashboard | Tài khoản Admin; dữ liệu hóa đơn/lịch hoàn tất; khoảng ngày bao trùm timestamp dữ liệu | Mở Overview, chọn khoảng ngày và nhóm thời gian. | Hiển thị doanh thu hóa đơn đã PAID và lượt khám theo định nghĩa trong dashboard; khoảng không dữ liệu hiển thị số 0/trạng thái rỗng rõ ràng. | Dùng khoảng ngày bao gồm dữ liệu seed; không sửa số liệu để “đẹp” kết quả. |

## Kiểm tra trước buổi demo

- [ ] Chạy migrations/seed trên database demo; xác nhận 5 bệnh nhân, 5 dịch vụ, lịch, EMR và `DEMO-INV-001` có liên kết.
- [ ] Đặt mật khẩu riêng cho account demo; xác nhận từng role đăng nhập được.
- [ ] Thử booking với giờ trống; thử một khung giờ trùng để xác nhận API từ chối.
- [ ] Xác nhận consent mặc định false; chỉ bật consent trên hồ sơ synthetic khi minh họa có phê duyệt và Gemini sẵn sàng.
- [ ] Thử summary và reminder preview với mock/test hoặc Gemini đã cấu hình; preview không được gọi Twilio.
- [ ] Xác nhận hóa đơn demo ban đầu là `ISSUED`; thử cash payment trên database demo mới. Seed không xóa/reset lịch sử payment; nếu hóa đơn đã thanh toán, giữ nguyên dữ liệu đó và chuẩn bị database demo cô lập mới với đường dẫn khác cho lượt trình diễn sau.
- [ ] Xác nhận chatbot và dashboard tải dữ liệu; chọn khoảng ngày chứa bản ghi seed.
- [ ] Chạy `python manage.py send_follow_up_reminders --dry-run` nếu cần kiểm tra scheduler eligibility; dry-run chỉ đếm bản ghi, **không tạo nội dung preview và không gửi**.
- [ ] Không chạy lệnh gửi SMS thật trong buổi demo; không cấu hình số nhận thật cho dữ liệu seed.
- [ ] Ghi nhận các bước AI cần API key là phụ thuộc cấu hình, không trình bày mock là kết quả từ dịch vụ thật.

## Trạng thái kiểm thử và giới hạn

Seed idempotent và API/UI reminder preview có test tự động; các test provider dùng mock, không chứng minh kết nối Gemini/Twilio thật. Chỉ xác nhận buổi demo trực tiếp hoàn chỉnh sau khi nhóm chạy đủ checklist trên môi trường demo và điền tên người trình bày. Video dự phòng thuộc Lát 4; tổng duyệt cuối cùng thuộc Lát 5.
