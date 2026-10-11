# Prompt: Tinh chỉnh prompt từ Zero-Shot sang Few-Shot

## Kỹ thuật minh họa

Refinement: chỉ thay đổi một yếu tố mỗi lần và so sánh trước/sau.

## Prompt sử dụng

[Instructions]

Hãy tinh chỉnh prompt chatbot cung cấp thông tin dịch vụ nha khoa từ phiên bản zero-shot sang phiên bản few-shot để giảm lỗi trả lời về dịch vụ không hoạt động hoặc thông tin không có trong nguồn.

[Prompt v1 - Zero-shot]

```text
Khách hàng hỏi: {{customer_question}}.
Dữ liệu dịch vụ đã truy xuất: {{dental_service_data}}.
Hãy trả lời câu hỏi của khách hàng.
```

[Vấn đề quan sát]

- Có lúc AI cung cấp thông tin về dịch vụ đang không hoạt động.
- Có lúc AI tự đoán giá hoặc thời lượng khi dữ liệu thiếu.
- Định dạng câu trả lời không nhất quán.

[Requirements]

- Chỉ tinh chỉnh bằng cách thêm ví dụ few-shot và định dạng đầu ra.
- Giữ nguyên mục tiêu chính của prompt là trả lời câu hỏi thông tin dịch vụ dựa trên dữ liệu được cung cấp.
- Thêm 2 ví dụ: một ví dụ có dịch vụ phù hợp, đang hoạt động và có đủ thông tin; một ví dụ không có dịch vụ phù hợp hoặc dữ liệu truy xuất không đủ.
- Không thêm dữ liệu nhạy cảm; chỉ dùng dữ liệu dịch vụ giả lập.
- Các ví dụ không được đưa ra chẩn đoán hoặc khuyến nghị điều trị.

[Output Format]

Trả về:

1. Prompt v2 đã tinh chỉnh.
2. Bảng giải thích thay đổi so với v1.
3. 5 test case dùng để so sánh v1 và v2.
4. Tiêu chí quyết định v2 tốt hơn v1, gồm tính chính xác theo nguồn, cách xử lý dữ liệu thiếu, tính nhất quán định dạng và tuân thủ giới hạn không chẩn đoán.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `01-Vi-du-prompt.md` thì file kết quả phải là `01-Vi-du-prompt_ket_qua.md`.
