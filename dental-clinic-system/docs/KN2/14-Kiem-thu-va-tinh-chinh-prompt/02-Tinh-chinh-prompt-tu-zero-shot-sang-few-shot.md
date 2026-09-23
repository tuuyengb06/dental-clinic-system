# Prompt: Tinh chỉnh prompt tư vấn dịch vụ nha khoa từ Zero-Shot sang Few-Shot

## Kỹ thuật minh họa
Refinement: Chỉ thay đổi một yếu tố mỗi lần (thêm ví dụ vài lượt - Few-Shot prompting) và so sánh chất lượng phản hồi trước/sau để kiểm soát độ chính xác thông tin y tế & lịch hẹn.

## Prompt sử dụng

[Instructions]
Hãy tinh chỉnh prompt chatbot tư vấn dịch vụ và đặt lịch khám nha khoa từ phiên bản Zero-Shot sang phiên bản Few-Shot để khắc phục lỗi gợi ý dịch vụ hết/kín lịch và giảm nguy cơ tư vấn sai thông tin chuyên môn y tế.

[Prompt v1 - Zero-shot]
"Nhu cầu bệnh nhân: {{patient_need}}. Dữ liệu dịch vụ & Lịch rảnh bác sĩ: {{service_and_schedule_table}}. Hãy gợi ý dịch vụ phù hợp và đề xuất tối đa 2 khung giờ khám."

[Vấn đề quan sát]
- AI có lúc gợi ý lịch hẹn rơi vào khung giờ bác sĩ đã kín lịch (slot_status = "Full").
- AI đưa ra chẩn đoán lâm sàng khẳng định hoặc tư vấn dùng thuốc khi dữ liệu triệu chứng của bệnh nhân chưa đầy đủ.
- Định dạng câu trả lời không nhất quán, thiếu thông tin lưu ý an toàn y tế cơ bản.

[Requirements]
- Tinh chỉnh bằng cách thêm các ví dụ minh họa (Few-Shot Examples) và quy định định dạng đầu ra chuẩn.
- Giữ nguyên mục tiêu cốt lõi: Tư vấn dịch vụ dựa đúng trên dữ liệu context và hướng dẫn đặt lịch.
- Bổ sung tối thiểu 2 ví dụ cụ thể: 
  1. Một ví dụ có dịch vụ và khung giờ khả dụng.
  2. Một ví dụ khi khung giờ/dịch vụ bị kín lịch hoặc bệnh nhân mô tả triệu chứng cấp bách cần khám ngay thay vì tự điều trị.
- Không đưa dữ liệu cá nhân bệnh nhân thực tế (PHI/PII) vào ví dụ.

[Output Format]
Trả về bài viết Markdown gồm:
1. Prompt v2 đã tinh chỉnh (kèm Few-Shot examples).
2. Bảng so sánh & giải thích các điểm thay đổi chính so với v1.
3. 5 test case dùng để so sánh hiệu năng giữa v1 và v2.
4. Tiêu chí quyết định v2 đạt yêu cầu để thay thế v1.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `31-Tinh-chinh-prompt-zero-shot-sang-few-shot-nha-khoa.md` thì file kết quả phải là `31-Tinh-chinh-prompt-zero-shot-sang-few-shot-nha-khoa_ket_qua.md`.