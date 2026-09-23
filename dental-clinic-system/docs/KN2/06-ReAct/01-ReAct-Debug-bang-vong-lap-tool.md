# Prompt: Debug hệ thống nha khoa bằng vòng lặp ReAct

## Kỹ thuật minh họa
ReAct Framework: Kết hợp Suy luận (Reasoning), Hành động (Acting) và Quan sát (Observation) cho các tác vụ cần truy vết bug, chạy lệnh, kiểm tra log và sửa lỗi theo chu kỳ phản hồi.

## Prompt sử dụng

Bạn là trợ lý lập trình senior làm việc theo chu trình ReAct (Reasoning - Acting - Observation). Hãy debug lỗi bất đồng bộ dữ liệu lịch hẹn và khấu trừ tồn kho vật tư y tế trong Hệ thống Quản lý Phòng khám Nha khoa Tích hợp AI bằng vòng lặp suy luận và hành động liên tục.

Bối cảnh:
- Backend hệ thống xây dựng bằng Python (FastAPI/Django) hoặc Node.js (NestJS).
- Có phân hệ quản lý Lịch hẹn (được đặt tự động bởi Chatbot AI hoặc Lễ tân), Bệnh án điện tử (EMR) và Quản lý Kho vật tư (thuốc tê, mắc cài, implant...).
- Lỗi phát sinh: Khi bác sĩ hoàn tất đợt điều trị hoặc cập nhật phác đồ, lượng vật tư y tế trừ vào kho bị sai lệch (trừ lặp lại nhiều lần) HOẶC lịch hẹn do AI đặt bị trùng ghế khám/bác sĩ.
- Bạn được phép đề xuất các hành động cụ thể như: kiểm tra cấu trúc file, kiểm tra SQL queries, đọc log hệ thống, chạy unit test / integration test, thêm log debug và sửa code.

Quy tắc ReAct bắt buộc:
- Lặp lại qua từng Vòng (Iteration) bao gồm:
  - **Thought (Suy luận):** Nêu giả thuyết ngắn gọn về nguyên nhân gây lỗi dựa trên thông tin hiện có.
  - **Action (Hành động):** Nêu thao tác cụ thể cần thực hiện (vd: kiểm tra file `services/dental_inventory.py`, kiểm tra hàm `update_treatment_plan()`).
  - **Observation (Quan sát):** Mô tả kết quả kỳ vọng hoặc giả lập log/error message thu được sau hành động.
- Tuyệt đối không kết luận vội vã khi chưa trải qua đủ các bước quan sát dữ liệu.
- Khi xác định đúng nguyên nhân gốc rễ (Root Cause), hãy đề xuất bản sửa lỗi nhỏ nhất (minimal patch) kèm theo Test case xác nhận để ngăn chặn regression.

Đầu vào cần tôi cung cấp thêm cho bạn:
- Cấu trúc thư mục nguồn (Source Code Tree) của backend nha khoa.
- Đoạn code xử lý dịch vụ/bệnh án/kho vật tư bị nghi ngờ.
- Mã lỗi (Error Stack Trace), log hệ thống hoặc kịch bản Test đang báo thất bại (Failed).

Định dạng đầu ra:
1. Kế hoạch ReAct tổng quan ban đầu.
2. Chi tiết từng vòng lặp ReAct (Thought -> Action -> Observation).
3. Nguyên nhân gốc rễ (Root Cause Analysis).
4. Bản sửa lỗi đề xuất (Code Patch / Pull Request).
5. Kịch bản Test xác nhận sau khi sửa lỗi.

---

## Yêu cầu ghi kết quả

Khi thực hiện prompt này, hãy ghi toàn bộ kết quả đầu ra vào một file Markdown mới trong cùng thư mục với file prompt.

Tên file kết quả phải giữ nguyên tên file prompt hiện tại và thêm hậu tố `_ket_qua` trước phần mở rộng `.md`.

Ví dụ: nếu file prompt là `13-Debug-react-he-thong-nha-khoa.md` thì file kết quả phải là `13-Debug-react-he-thong-nha-khoa_ket_qua.md`.