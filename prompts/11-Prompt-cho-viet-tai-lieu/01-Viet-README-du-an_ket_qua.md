# Hệ thống quản lý nha khoa tích hợp AI

> README khung cho bản demo. Tài liệu đầu vào cho biết các công nghệ có thể lựa chọn nhưng chưa xác nhận stack/lệnh chạy thực tế. Thay placeholder sau khi đối chiếu repository; không xem ví dụ dưới đây là cấu hình đã kiểm thử.

## 1. Tên dự án

Hệ thống quản lý nha khoa tích hợp AI.

## 2. Mô tả ngắn

Ứng dụng dự kiến hỗ trợ quản lý hoạt động phòng khám nha khoa và một số tác vụ AI hỗ trợ. Chức năng thực tế phụ thuộc vào phiên bản được triển khai.

## 3. Chức năng quản lý chính

- Hồ sơ bệnh nhân, lịch hẹn, hồ sơ khám/điều trị.
- Danh mục dịch vụ và kế hoạch điều trị.
- Hóa đơn, thanh toán, vật tư và báo cáo.
- Quản lý người dùng, vai trò và quyền truy cập.

Phạm vi chi tiết, trạng thái, quy trình hủy/hoàn và quyền của từng vai trò: **cần bổ sung từ đặc tả đã duyệt**.

## 4. Chức năng AI và giới hạn

- Chatbot cung cấp thông tin dịch vụ từ nội dung phòng khám đã phê duyệt.
- Hỗ trợ tóm tắt thông tin khám hoặc tạo nội dung để bác sĩ/người có thẩm quyền xem xét.
- Hỏi đáp dữ liệu hoạt động tổng hợp theo quyền.

AI chỉ hỗ trợ; không chẩn đoán, quyết định điều trị hoặc thay thế bác sĩ. Nội dung chuyên môn phải được người có thẩm quyền kiểm tra trước khi sử dụng.

## 5. Công nghệ sử dụng

| Thành phần | Tình trạng |
|---|---|
| Backend | Python; framework FastAPI/Flask/Django — cần xác nhận |
| Frontend | React/Vue/HTML-CSS-JavaScript — cần xác nhận |
| Database | SQLite được nêu cho demo; schema/phiên bản cần xác nhận |
| AI | Nhà cung cấp/model cần xác nhận |

## 6. Cấu trúc thư mục đề xuất

```text
project/
├── backend/
├── frontend/
├── database/
├── prompts/
├── tests/
├── docs/
├── .env.example
└── README.md
```

Đây là cấu trúc gợi ý; thay bằng cấu trúc repository thực tế.

## 7. Cài đặt và chạy local

**Chưa có lệnh đã xác nhận.** Sau khi biết framework/package manager, bổ sung:

```text
<lệnh cài dependencies của dự án>
<lệnh khởi tạo database/migration đã được xác nhận>
<lệnh chạy backend đã được xác nhận>
<lệnh chạy frontend đã được xác nhận>
```

Không chạy lệnh placeholder như lệnh thực tế. Lưu ý yêu cầu phiên bản Python/Node, cổng và cách nạp biến môi trường sau khi xác minh.

## 8. Cấu hình môi trường

Tạo `.env` cục bộ từ `.env.example` nếu dự án có hướng dẫn. Không commit `.env`.

```dotenv
AI_API_KEY=demo-placeholder-not-a-real-key
AI_MODEL=replace-after-provider-selection
DATABASE_URL=sqlite:///./demo.db
```

Giá trị trên chỉ là placeholder minh họa, không phải secret thật hoặc endpoint đã cấu hình. Dùng secret manager/biến môi trường phù hợp cho triển khai.

## 9. Dữ liệu mẫu và tài khoản demo

Chỉ dùng dữ liệu giả lập/đã khử định danh. Thông tin đăng nhập demo **chưa được cung cấp**; không đặt mật khẩu mặc định trong tài liệu. Bổ sung username/password giả sau khi tạo tài khoản demo an toàn và ghi rõ cách đổi/xóa.

## 10. Kiểm thử

Lệnh test **cần xác nhận theo cấu hình dự án**: `<lệnh test đã được xác nhận>`. Bộ test nên bao gồm lịch hẹn, hồ sơ điều trị, hóa đơn/thanh toán, quyền truy cập, tồn kho và các trường hợp AI dữ liệu thiếu/sai định dạng. Ghi chính xác kết quả đã chạy; không khẳng định test pass khi chưa chạy.

## 11. Bảo mật và quyền riêng tư

- Phân quyền theo vai trò và giới hạn hồ sơ bệnh nhân/hồ sơ sức khỏe.
- Chỉ gửi dữ liệu tối thiểu đến AI; không gửi định danh hoặc hồ sơ sức khỏe nếu không cần.
- Không ghi API key, mật khẩu hoặc dữ liệu cá nhân vào source, prompt mẫu, log hay test fixture.
- Nội dung AI phải bám nguồn; AI không thay thế bác sĩ; chuyên môn cần được người có thẩm quyền duyệt.
- Xác định consent, retention, nơi xử lý dữ liệu và chính sách truy cập với bên phụ trách; nội dung cần được xác nhận, không tự tuyên bố tuân thủ luật/chuẩn cụ thể.
