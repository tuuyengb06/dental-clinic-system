# Dental Management System (DMS)

MVP runnable cho phòng khám nha khoa, gồm Django REST Framework backend và React/Vite frontend.

Tài liệu kiến trúc hiện trạng, ERD và hai sequence AI (được đánh dấu rõ là luồng đề xuất chưa triển khai) nằm tại [docs/architecture-and-design.md](docs/architecture-and-design.md).

Bộ slide trình bày dự án 13 trang, có kiến trúc, ERD rút gọn, ảnh chụp giao diện demo và kịch bản phân vai gợi ý 10 phút, nằm tại [docs/project-presentation.pptx](docs/project-presentation.pptx). Hai luồng tóm tắt EMR và nhắc tái khám bằng AI được ghi rõ là đề xuất, chưa triển khai. Trên Windows có Microsoft PowerPoint, có thể tạo lại slide bằng `powershell -ExecutionPolicy Bypass -File docs/generate-project-presentation.ps1`.

## 1. Cài đặt yêu cầu

- Python 3.11 hoặc mới hơn
- Node.js 20 hoặc mới hơn
- npm 10 hoặc mới hơn

## 2. Khởi chạy backend

```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py seed_dental_data
python manage.py runserver 8000
```

Backend chạy tại `http://127.0.0.1:8000`.

Kiểm tra nhanh: mở `http://127.0.0.1:8000/api/v1/health/` và xác nhận response có `status: ok`.

Để tạo QR chuyển khoản cho bản demo, cấu hình thông tin tài khoản nhận trong PowerShell trước khi chạy backend (không commit thông tin tài khoản thật):

```powershell
$env:DMS_VIETQR_BANK_ID = "<bank code or BIN>"
$env:DMS_VIETQR_ACCOUNT_NUMBER = "<account number>"
$env:DMS_VIETQR_ACCOUNT_NAME = "<account holder name>"
python manage.py runserver 8000
```

Nếu chưa cấu hình đủ ba biến, API QR trả về `503` và không tạo giao dịch chờ. Ảnh QR được tải từ dịch vụ VietQR; URL chứa số tiền, mã hóa đơn và thông tin tài khoản nhận.

`python manage.py migrate` là cách khởi tạo/cập nhật database được khuyến nghị và là nguồn schema chuẩn. `backend/schema.sql` chỉ là schema SQLite nền cũ gồm 13 bảng clinic ban đầu, không phải bản dump đầy đủ của toàn bộ model/migration hiện tại. Nếu cần dùng quy trình bootstrap SQL cũ trên database SQLite mới, chạy các lệnh sau trong thư mục `backend`; các migration Django tiếp theo vẫn cần chạy để thêm/cập nhật schema:

```powershell
python manage.py migrate contenttypes
python manage.py migrate auth
python -c "import sqlite3; sqlite3.connect('db.sqlite3').executescript(open('schema.sql', encoding='utf-8').read())"
python manage.py migrate clinic --fake
python manage.py migrate
python manage.py seed_dental_data
```

Không chạy bước SQL này trên database đã có dữ liệu cần giữ; dùng migration Django thông thường để cập nhật database hiện có.

## 3. Khởi chạy frontend

Mở một PowerShell mới:

```powershell
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

Máy chạy frontend/backend và người cùng nhóm cần dùng chung một mạng Wi-Fi/LAN. Mở URL Vite hiển thị trong terminal trên máy chủ, rồi cho người kia truy cập `http://<IP-máy-chủ>:5173` (lấy địa chỉ IPv4 bằng `ipconfig`). Nếu Windows Firewall hỏi, chỉ cho phép trên mạng Private. Vite chuyển tiếp `/api` đến backend trên cùng máy ở `http://127.0.0.1:8000`; vì vậy cả hai người dùng cùng một backend và database SQLite trên máy chủ. Chỉ dùng cách này trên mạng tin cậy cho demo, không mở development server ra Internet. Tailwind CSS v4 đã được tích hợp với Vite; Lucide Icons được dùng làm bộ biểu tượng giao diện. Khi triển khai riêng frontend và backend, đặt `VITE_API_BASE_URL` thành URL gốc API.

Đăng nhập bằng username/password của tài khoản Django có hồ sơ clinic. Tài khoản quản trị demo có username `admin`; đặt mật khẩu bằng `python manage.py changepassword admin` hoặc cấu hình `DMS_SEED_ADMIN_PASSWORD` trước khi seed. Mật khẩu của tài khoản bác sĩ/lễ tân được đặt bằng `python manage.py changepassword doctor1`, `doctor2` hoặc `receptionist1`. JWT access/refresh token được lưu trong LocalStorage và tự refresh khi access token hết hạn.

Sidebar hiển thị mục theo role `ADMIN`, `DENTIST` hoặc `RECEPTIONIST`. Chỉ ADMIN được tạo/sửa/ngừng dịch vụ; các hồ sơ bác sĩ có thể xem trong danh mục Doctors.

## 4. Dữ liệu demo

Các migration Django hiện tạo model nghiệp vụ trong `clinic` và `appointments`, gồm danh mục bệnh nhân/bác sĩ/dịch vụ, ca làm, lịch hẹn, EMR, kế hoạch điều trị, hóa đơn, giao dịch và dữ liệu đối soát QR. `clinic.Appointment`/`TreatmentPlan`/`TreatmentItem` là các model legacy; lịch và EMR của API hiện hành dùng `appointments.Appointment`/`MedicalRecord`. `backend/schema.sql` chỉ phản ánh 13 bảng clinic nền ban đầu; các thay đổi tiếp theo được quản lý bằng migration Django. Các bảng quản trị mặc định của Django (`auth`, `admin`, `sessions`) được tạo riêng bởi migration của Django.

Chạy `python manage.py migrate` để tạo schema từ migration. Sau đó chạy `python manage.py seed_dental_data` để tạo:

- 32 mã răng người lớn `A01` đến `A32`.
- 20 mã răng trẻ em `C01` đến `C20`.
- 1 tài khoản quản trị, 2 bác sĩ và 1 lễ tân (các tài khoản demo không có mật khẩu sử dụng được mặc định).
- 5 bệnh nhân, danh mục dịch vụ nha khoa cơ bản, lịch hẹn, kế hoạch điều trị và hóa đơn mẫu.

Để cấp mật khẩu cho tài khoản quản trị được seed, đặt biến môi trường `DMS_SEED_ADMIN_PASSWORD` trước khi chạy lệnh seed; hoặc dùng `python manage.py changepassword admin`. Nếu database đã có tài khoản demo `dms_admin`, lệnh seed sẽ đổi tên tài khoản đó thành `admin`.

## 5. API chính

- `POST /api/v1/auth/token/` (đăng nhập, lấy JWT)
- `POST /api/v1/auth/token/refresh/` (làm mới JWT)
- `GET /api/v1/auth/me/` (hồ sơ người dùng và role, cần JWT)
- `GET/POST /api/v1/patients/` (hồ sơ gồm ngày sinh, kiểu răng, tiền sử bệnh và dị ứng)
- `GET /api/v1/patients/?search=<mã|tên|điện thoại>` (tra cứu hồ sơ bệnh nhân; yêu cầu role Admin hoặc Receptionist)
- `GET/POST /api/v1/appointments/` (danh sách/đặt lịch; giờ hẹn phải nằm trong ca làm của bác sĩ và không trùng lịch)
- `POST /api/v1/appointments/{id}/cancel/` (lễ tân/Admin hủy lịch Pending hoặc Confirmed; lịch Completed hoặc đã Cancelled bị từ chối)
- `GET/POST /api/v1/schedules/` (xem/đặt ca làm theo bác sĩ, ngày và giờ; không cho phép ca chồng nhau)
- `GET /api/v1/teeth/` (danh mục răng để lập hồ sơ bệnh án)
- `GET/POST/PATCH /api/v1/medical-records/` (bác sĩ lập/cập nhật chẩn đoán, hướng điều trị, răng và dịch vụ chỉ định; mỗi hồ sơ gắn với một lịch hẹn)
- `GET /api/v1/invoices/` (lịch sử hóa đơn và thông tin giao dịch, chỉ Admin/Lễ tân)
- `GET /api/v1/invoices/available-records/` (hồ sơ có dịch vụ được chỉ định nhưng chưa lập hóa đơn, chỉ trả thông tin cần thiết cho thu ngân)
- `POST /api/v1/invoices/` (tạo một hóa đơn cho hồ sơ khám với mọi dịch vụ chỉ định và số lượng; backend lấy đơn giá danh mục, tự tính thành tiền/tổng tiền, phát hành trạng thái `ISSUED` chưa thanh toán; không cho lập trùng hóa đơn cho một hồ sơ)
- `POST /api/v1/invoices/{id}/pay-cash/` (lễ tân/Admin xác nhận đã nhận đủ tiền mặt cho hóa đơn `ISSUED`; tạo một giao dịch `COMPLETED`, cập nhật hóa đơn thành `PAID`, từ chối thanh toán lặp)
- `POST /api/v1/invoices/{id}/pay-qr/` (lễ tân/Admin tạo hoặc xem lại VietQR cho hóa đơn chưa thanh toán; tạo một giao dịch `BANK_TRANSFER` ở trạng thái `PENDING`, không cập nhật hóa đơn thành `PAID`)
- `POST /api/v1/invoices/{id}/reconcile-qr/` (lễ tân/Admin đối soát thủ công sau khi kiểm tra tài khoản nhận; yêu cầu mã tham chiếu giao dịch, số tiền khớp chính xác và xác nhận đã kiểm tra; lưu người xác nhận/thời điểm, từ chối mã tham chiếu trùng, rồi cập nhật giao dịch và hóa đơn nguyên tử)
- `POST /api/v1/invoices/{id}/cancel-qr/` (lễ tân/Admin đóng giao dịch QR `PENDING` chỉ sau khi xác nhận đã kiểm tra tài khoản và chưa nhận tiền; lưu người/thời điểm hủy, giữ lịch sử và mở lại khả năng thử QR hoặc thu tiền mặt; không tự hết hạn giao dịch)
- `GET /api/v1/dashboard/analytics/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&group_by=auto|day|month` (chỉ Admin; tổng doanh thu từ tổng `total_amount` mỗi hóa đơn `PAID` theo `issued_at`, tổng lượt khám từ lịch `Completed` theo `appointment_date`; ngày đầu/cuối bao gồm trọn ngày, timezone `Asia/Ho_Chi_Minh`, tự nhóm ngày cho khoảng tối đa 90 ngày và nhóm tháng cho khoảng dài hơn)
- `POST /api/ai/chat` (public chatbot chỉ tra giá dịch vụ đang hoạt động và giờ bắt đầu còn trống theo ca làm/lịch hẹn; body chỉ nhận `{"question":"..."}`, tối đa 500 ký tự; giới hạn 30 câu hỏi/IP mỗi giờ)
- `GET/POST /api/v1/services/` (`POST/PATCH/DELETE` chỉ dành cho ADMIN; DELETE sẽ ngừng dịch vụ)
- `GET /api/v1/doctors/`
- `GET /api/v1/health/` (public health check; các API nghiệp vụ khác cần JWT)

Frontend dùng thống nhất các endpoint API v1. Role từ `/auth/me/` được chuẩn hóa thành `ADMIN`, `DENTIST` hoặc `RECEPTIONIST`. Lễ tân/Admin quản lý ca làm và đặt lịch; bác sĩ chỉ xem các lịch của mình và chỉ được lập bệnh án cho các lịch được giao. Chỉ ADMIN được ghi danh mục dịch vụ. Môi trường local mặc định dùng SQLite; chọn SQL Server bằng `DMS_DB_ENGINE=mssql` cùng các biến `DMS_DB_*`.

Màn hình lịch hẹn hỗ trợ xem theo ngày/tuần, chuyển khoảng thời gian và lọc theo bác sĩ; ca làm và lịch hẹn được đọc từ `/api/v1/schedules/` và `/api/v1/appointments/`. Ngoài giờ làm được phân biệt trực quan với ca làm và lịch hẹn. Thao tác đặt lịch hoặc quản lý ca hiện có trên màn hình vẫn là luồng hiện hữu, không thuộc phạm vi hoàn thiện đặt/hủy lịch của tính năng xem lịch.

Luồng đặt lịch trên giao diện dành cho lễ tân/Admin, gửi `patient`, `doctor`, `service`, `appointment_date` và lý do khám trong `notes` tới `POST /api/v1/appointments/`. Backend xác thực giờ làm, thời lượng dịch vụ và xung đột lịch; giao diện chỉ xác nhận thành công sau khi API tạo lịch, sau đó chuyển tới ngày hẹn để thấy lịch mới. API hiện yêu cầu tài khoản nhân viên đã đăng nhập để tạo lịch, nên chưa hỗ trợ bệnh nhân tự đặt lịch.

Tại màn hình lịch, lễ tân/Admin có thể yêu cầu hủy lịch Pending hoặc Confirmed sau khi xác nhận trong hộp thoại. API trả bản ghi cập nhật; giao diện chỉ đổi trạng thái sau phản hồi thành công và giữ thông báo lỗi nếu API từ chối hoặc mất kết nối. Các trạng thái được phép hủy là quy ước hiện tại, cần được nhóm trưởng xác nhận.

Tại màn hình `Billing`, Admin/Lễ tân chọn hồ sơ khám có dịch vụ đã chỉ định, nhập số lượng và xem tổng tạm tính trước khi tạo hóa đơn. Backend chỉ chấp nhận đầy đủ danh sách dịch vụ của hồ sơ, lấy giá hiện tại từ danh mục thay vì tin giá/tổng do client gửi, lưu giá mô tả tại thời điểm lập hóa đơn, và giới hạn một hóa đơn cho mỗi hồ sơ khám. Hóa đơn mới có trạng thái `ISSUED`, số đã thanh toán bằng 0. Lễ tân/Admin có thể xác nhận đã nhận đủ tiền mặt một lần; API lưu người nhận, thời điểm, số tiền, phương thức và trạng thái giao dịch `COMPLETED` rồi cập nhật hóa đơn thành `PAID` trong cùng transaction. Với chuyển khoản QR, cấu hình `DMS_VIETQR_BANK_ID`, `DMS_VIETQR_ACCOUNT_NUMBER` và `DMS_VIETQR_ACCOUNT_NAME` trong môi trường backend; API VietQR chỉ tạo ảnh/mã chuyển tiền và giao dịch `PENDING`, không xác minh tiền đã vào tài khoản. Nếu dùng số tài khoản thật, QR hướng tiền tới tài khoản thật và có thể phát sinh giao dịch thật; cấu hình demo không tự tạo sandbox ngân hàng. Để ghi nhận thanh toán, nhân viên phải tự kiểm tra tài khoản/sao kê ngân hàng, so khớp chính xác số tiền và mã tham chiếu giao dịch, rồi xác nhận trong giao diện. Hệ thống lưu mã tham chiếu duy nhất, người dùng xác nhận và thời điểm; việc này là đối soát thủ công, không phải webhook hay xác minh tự động từ ngân hàng. Nếu tài khoản đã được kiểm tra và không có tiền vào, nhân viên có thể hủy giao dịch `PENDING` (lưu người/thời điểm); sau đó được tạo QR mới hoặc nhận tiền mặt, trong khi lần chuyển cũ vẫn nằm trong lịch sử. Không tự hủy theo bộ đếm thời gian vì giao dịch ngân hàng có thể đến trễ. Không xác nhận dựa trên QR hoặc lời báo của bệnh nhân. Trong thời gian giao dịch đang chờ, giao diện khóa xác nhận thu tiền mặt để tránh ghi nhận chồng. Không lưu số tài khoản nhận trong mã nguồn.

QR được tạo thành ảnh qua `img.vietqr.io`; yêu cầu ảnh chứa mã ngân hàng, số tài khoản nhận, tên chủ tài khoản, số tiền và nội dung chuyển khoản. Do đó dịch vụ VietQR nhận các thông tin này khi tải ảnh QR. Không cấu hình tài khoản thật nếu chưa chấp thuận việc chia sẻ thông tin đó với nhà cung cấp QR; có thể chuyển sang tạo QR cục bộ hoặc một nhà cung cấp được phê duyệt trước khi triển khai thật.

Chatbot ở góc màn hình dùng bộ phân loại câu hỏi và truy vấn dữ liệu hệ thống trực tiếp; hiện không gọi mô hình AI/dịch vụ bên ngoài và không gửi lịch sử chat sang bên thứ ba. Chatbot chỉ cung cấp giá dịch vụ đang hoạt động và khung giờ gợi ý theo ca làm/lịch hẹn hiện có (thời lượng dịch vụ, bước gợi ý 15 phút); khi hỏi lịch cần có ngày (có thể ghi `ngày/tháng`, hệ thống hiểu là năm hiện tại) và dịch vụ. Không có thao tác đặt lịch, không đọc/tiết lộ hồ sơ bệnh nhân, không tư vấn chẩn đoán; câu hỏi ngoài phạm vi hoặc tình huống y tế cần liên hệ lễ tân/cơ sở y tế. Khung giờ trả về không phải xác nhận giữ chỗ và cần được lễ tân kiểm tra lại. Nguồn dữ liệu không truy cập được sẽ trả thông báo thử lại/liên hệ lễ tân thay vì tự bịa câu trả lời.

Dashboard Overview chỉ dành cho Admin. Doanh thu dùng tổng giá trị `total_amount` của từng hóa đơn trạng thái `PAID`, nhóm theo ngày phát hành hóa đơn (`issued_at`); hóa đơn chưa thanh toán và QR `PENDING` không được tính. Lượt khám là số lịch hẹn trạng thái `Completed`, nhóm theo ngày/giờ hẹn (`appointment_date`), không phải số hóa đơn hay số dịch vụ. API dùng khoảng ngày bao gồm cả hai đầu theo `Asia/Ho_Chi_Minh`, trả cả các ngày/tháng không có dữ liệu với số 0; mặc định nhóm theo ngày nếu khoảng chọn dưới 90 ngày, nếu không nhóm theo tháng. Có thể chọn rõ nhóm ngày/tháng; nhóm ngày giới hạn tối đa một năm và khoảng tra cứu tối đa mười năm.

## 6. Build kiểm tra

```powershell
cd frontend
npm run build
```

Backend có thể kiểm tra bằng:

```powershell
cd backend
python manage.py check
```

## 7. Chụp ảnh minh chứng

1. Chạy backend ở một terminal và frontend ở terminal thứ hai.
2. Mở `http://127.0.0.1:5173`.
3. Chụp Dashboard.
4. Chọn `Patients` để chụp danh sách hồ sơ.
5. Chọn `Tooth chart`, thử `Adult · 32` và `Child · 20`, chụp cả hai trạng thái.
6. Đăng nhập role lễ tân/Admin, mở `Reception` để chụp form tiếp nhận; vào `Appointments` để tạo ca làm và đặt hẹn.
7. Đăng nhập role bác sĩ, mở `EMR`, chọn lịch hẹn để xem bệnh nhân, thông tin dị ứng/tiền sử, nhập chẩn đoán và hướng điều trị, chọn răng trên sơ đồ cung hàm, chọn dịch vụ rồi lưu hoặc cập nhật hồ sơ.
8. Chọn `Billing` để chụp phần công nợ.

## Phạm vi MVP

Đã có giao diện tiếp nhận tra cứu hồ sơ theo mã bệnh nhân, họ tên hoặc số điện thoại, hiển thị thông tin định danh, ngày sinh, kiểu răng, dị ứng, tiền sử bệnh và các lịch hẹn hiện có. API tra cứu trả lỗi đầu vào rõ ràng cho truy vấn trống hoặc ký tự không hợp lệ. EMR lưu chẩn đoán, hướng điều trị dạng ghi chú, răng được chọn và danh sách dịch vụ qua `/api/v1/medical-records/`; API chưa cung cấp luồng TreatmentPlan/TreatmentItem riêng để lưu số lượng hoặc gắn riêng từng dịch vụ với từng răng. Hóa đơn được tạo từ các dịch vụ chỉ định lưu trên hồ sơ khám, hỗ trợ đơn giá/số lượng/thành tiền và trạng thái chưa thanh toán; giao diện cũng hỗ trợ xác nhận thanh toán đủ bằng tiền mặt, lưu giao dịch và cập nhật hóa đơn sang `PAID`. Chuyển khoản QR, chatbot AI, ảnh radiograph và dashboard doanh thu vẫn ngoài phạm vi.
