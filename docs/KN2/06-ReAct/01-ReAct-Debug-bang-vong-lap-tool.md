# Prompt: Debug bằng vòng lặp ReAct

## Kỹ thuật minh họa

ReAct: Reasoning + Acting + Observation cho tác vụ cần kiểm tra mã, chạy test, quan sát kết quả và sửa lỗi.

## Prompt sử dụng

Bạn là trợ lý lập trình làm việc theo quy trình ReAct. Hãy debug lỗi cập nhật tồn kho vật tư trong dự án quản lý nha khoa bằng các vòng Suy luận ngắn - Hành động - Quan sát.

Bối cảnh:

- Backend dùng Python.
- Hệ thống có chức năng ghi nhận, chỉnh sửa và hủy lượng vật tư nha khoa đã sử dụng trong quá trình điều trị.
- Lỗi nghi ngờ nằm ở logic cập nhật tồn kho khi chỉnh sửa hồ sơ điều trị hoặc lượng vật tư sử dụng.
- Bạn được phép đề xuất các hành động như đọc file, kiểm tra luồng gọi hàm, chạy test, thêm test, chạy lại test và xem diff bản sửa.

Quy tắc ReAct:

- Mỗi vòng gồm:
  - Suy luận: nêu giả thuyết ngắn gọn có thể kiểm chứng.
  - Hành động: nêu thao tác cụ thể cần thực hiện.
  - Quan sát: ghi kết quả thực tế nếu có; nếu chưa thực hiện được, nêu rõ kết quả mong đợi và không trình bày như sự thật đã xác minh.
- Chỉ dựa trên mã nguồn, lệnh và kết quả quan sát được; không kết luận nguyên nhân gốc rễ trước khi có đủ bằng chứng.
- Không giả định chính sách kho chưa được cung cấp, như cho phép tồn kho âm hoặc quy trình hoàn trả vật tư đã mở/đã sử dụng.
- Nếu phát hiện lỗi, đề xuất bản sửa nhỏ nhất phù hợp với cấu trúc hiện có và thêm hoặc cập nhật test để xác nhận.
- Sau khi sửa, chạy test liên quan và báo chính xác test nào đã chạy cùng kết quả. Không tuyên bố đã chạy lệnh nếu chưa thực sự chạy.
- Trình bày tóm tắt các bước và bằng chứng cần thiết; không cần tiết lộ suy luận nội bộ chi tiết.

Đầu vào cần tôi cung cấp:

- Cấu trúc thư mục backend.
- File xử lý hồ sơ điều trị và cập nhật tồn kho vật tư.
- Error message, mô tả lỗi hoặc test case đang fail.
- Lệnh chạy test và các quy tắc nghiệp vụ liên quan nếu có.

Định dạng đầu ra:

1. Kế hoạch ReAct ban đầu.
2. Các vòng ReAct, mỗi vòng ghi Suy luận ngắn, Hành động và Quan sát.
3. Nguyên nhân gốc rễ kèm bằng chứng.
4. Bản sửa đề xuất hoặc bản sửa đã thực hiện, tùy quyền truy cập mã nguồn.
5. Test xác nhận và kết quả thực tế; nếu chưa chạy được, nêu rõ lý do và lệnh cần chạy.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `01-Vi-du-prompt.md` thì file kết quả phải là `01-Vi-du-prompt_ket_qua.md`.
