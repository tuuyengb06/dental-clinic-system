# Quy trình quản lý prompt chatbot dịch vụ nha khoa

> Đề xuất tham khảo cho dự án sinh viên; không khẳng định tuân thủ tiêu chuẩn/pháp luật cụ thể.

## Cấu trúc thư mục gợi ý

```text
prompts/
└── dental-service-chatbot/
    ├── prompt.md
    ├── metadata.yaml
    ├── changelog.md
    ├── tests/
    │   ├── cases.yaml
    │   └── expected-results.md
    ├── evaluations/
    │   └── <version-or-date>/
    └── README.md
```

Không đưa API key, bệnh nhân thật hay hồ sơ sức khỏe thật vào source/tests/evaluations. Bộ dữ liệu kiểm thử nên là giả lập hoặc khử định danh.

## Bảng metadata

| Trường | Mục đích / ví dụ |
|---|---|
| `prompt_id` | ID ổn định, ví dụ `dental-service-faq` |
| `version` | `1.0.0` hoặc quy ước dự án đã chọn |
| `title` / `owner` | Tên prompt và nhóm chịu trách nhiệm |
| `purpose` | Trả lời FAQ dịch vụ từ nguồn đã duyệt |
| `input_schema` | Câu hỏi khách, chunks dịch vụ có trạng thái |
| `source_policy` | Chỉ nguồn nội dung dịch vụ được duyệt; ghi phiên bản nguồn nếu có |
| `output_format` | Các mục câu trả lời/thiếu dữ liệu/đề xuất liên hệ |
| `safety_constraints` | Không bịa, không chẩn đoán/điều trị, không lộ dữ liệu nhạy cảm |
| `model_config` | Provider/model/temperature đã cấu hình; tuyệt đối không chứa key |
| `test_suite` | Vị trí bộ kiểm thử và tiêu chí đánh giá |
| `approval_status` | draft/reviewed/approved/retired theo quy ước dự án |
| `approved_by` / `approved_at` | Người và thời điểm phê duyệt nếu có |

## Quy trình 6 giai đoạn

1. **Design:** xác định use case, người dùng, dữ liệu nguồn được phép, giới hạn y tế và format; viết prompt tách biệt mã nguồn.
2. **Testing & Evaluation:** lập bộ dữ liệu giả lập gồm happy path, thiếu/mâu thuẫn/inactive, injection và yêu cầu chẩn đoán; chấm bám nguồn, an toàn, nhất quán.
3. **Refinement:** phân loại lỗi, chỉnh prompt có kiểm soát, ghi rõ thay đổi và chạy lại bộ test hồi quy.
4. **Versioning & Cataloging:** gắn version, metadata, changelog; lưu bản đã duyệt và test tương ứng trong repository.
5. **Deployment:** chỉ triển khai bản đã qua review; kiểm tra quyền dữ liệu/truy xuất, cấu hình không chứa bí mật và có cách quay lui.
6. **Monitoring & Iteration:** theo dõi lỗi/feedback bằng log tối thiểu, tránh ghi prompt có dữ liệu nhạy cảm; định kỳ đánh giá, sửa và phát hành version mới.

## Quy tắc versioning

Quy ước tham khảo `MAJOR.MINOR.PATCH`:

- **MAJOR (v2.0):** thay đổi hành vi/format/guardrail có khả năng phá tương thích, ví dụ thay nguyên tắc trả lời hoặc schema đầu ra.
- **MINOR (v1.1):** thêm khả năng tương thích, ví dụ hỗ trợ thêm trường dữ liệu đã duyệt hoặc bổ sung nhánh từ chối.
- **PATCH (v1.0.1):** sửa lỗi diễn đạt/typo không đổi hành vi kỳ vọng.

Mỗi version có test kết quả và changelog; không ghi đè bản production khi chưa có so sánh/review.

## Checklist triển khai

- [ ] Prompt chỉ dùng nguồn dịch vụ đã duyệt; trạng thái inactive được xử lý đúng.
- [ ] Thiếu hoặc mâu thuẫn dữ liệu: không đoán; thông báo giới hạn.
- [ ] Người dùng yêu cầu chẩn đoán/điều trị: từ chối phần ngoài phạm vi và hướng dẫn gặp bác sĩ.
- [ ] Không gửi PII, hồ sơ sức khỏe hoặc dữ liệu thanh toán không cần thiết.
- [ ] Input/retrieved content được phân tách khỏi system instructions.
- [ ] Quyền truy cập và giới hạn dữ liệu truy xuất được kiểm tra ở backend.
- [ ] Output được kiểm tra định dạng/nội dung trước hiển thị.
- [ ] Bộ test version hiện tại chạy và kết quả được ghi đúng.
- [ ] Có người review/phê duyệt theo quy trình nhóm.
- [ ] Có version trước để rollback và xác định tiêu chí rollback.

## Ví dụ changelog

| Version | Thay đổi | Kiểm thử/ghi chú |
|---|---|---|
| v1.0.0 | Bản nháp đầu: chỉ trả lời từ nguồn dịch vụ đã duyệt; nêu thiếu dữ liệu | Chưa phê duyệt triển khai |
| v1.1.0 | Thêm xử lý rõ dịch vụ inactive và không đoán giá/thời lượng thiếu | Chạy lại test inactive/thiếu trường; cần review |
| v2.0.0 | Đổi format đầu ra và quy trình escalation câu hỏi chuyên môn | Breaking behavior; cần đánh giá toàn bộ regression trước deploy |
