# Dental Management System (DMS)

MVP runnable cho phòng khám nha khoa, gồm Django REST Framework backend và React/Vite frontend.

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

`python manage.py migrate` là cách khởi tạo database được khuyến nghị. Schema SQLite tương ứng với 13 bảng nghiệp vụ cũng có trong `backend/schema.sql`. Nếu cần khởi tạo bảng trực tiếp từ SQL trên database mới, chạy các lệnh sau trong thư mục `backend`:

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

Các migration Django tạo 13 bảng nghiệp vụ trong ứng dụng `clinic`: `Role`, `ClinicUser`, `Doctor`, `Patient`, `Appointment`, `Tooth`, `ToothCondition`, `Service`, `TreatmentPlan`, `TreatmentItem`, `Invoice`, `InvoiceItem` và `Payment`. Các bảng quản trị mặc định của Django (`auth`, `admin`, `sessions`) được tạo riêng bởi migration của Django.

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
- `GET/POST /api/v1/schedules/` (xem/đặt ca làm theo bác sĩ, ngày và giờ; không cho phép ca chồng nhau)
- `GET /api/v1/teeth/` (danh mục răng để lập hồ sơ bệnh án)
- `GET/POST /api/v1/medical-records/` (bác sĩ lập/cập nhật chẩn đoán, hướng điều trị, răng và dịch vụ chỉ định)
- `GET/POST /api/v1/invoices/`
- `GET/POST /api/v1/services/` (`POST/PATCH/DELETE` chỉ dành cho ADMIN; DELETE sẽ ngừng dịch vụ)
- `GET /api/v1/doctors/`
- `GET /api/v1/health/` (public health check; các API nghiệp vụ khác cần JWT)

Frontend dùng thống nhất các endpoint API v1. Role từ `/auth/me/` được chuẩn hóa thành `ADMIN`, `DENTIST` hoặc `RECEPTIONIST`. Lễ tân/Admin quản lý ca làm và đặt lịch; bác sĩ chỉ xem các lịch của mình và chỉ được lập bệnh án cho các lịch được giao. Chỉ ADMIN được ghi danh mục dịch vụ. Môi trường local mặc định dùng SQLite; chọn SQL Server bằng `DMS_DB_ENGINE=mssql` cùng các biến `DMS_DB_*`.

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
7. Đăng nhập role bác sĩ, mở `EMR` để nhập chẩn đoán, chọn răng và dịch vụ chỉ định.
8. Chọn `Billing` để chụp phần công nợ.

## Phạm vi MVP

Đã có giao diện tiếp nhận tra cứu hồ sơ theo mã bệnh nhân, họ tên hoặc số điện thoại, hiển thị thông tin định danh, ngày sinh, kiểu răng, dị ứng, tiền sử bệnh và các lịch hẹn hiện có. API tra cứu trả lỗi đầu vào rõ ràng cho truy vấn trống hoặc ký tự không hợp lệ. Lịch tuần/đặt lịch và hồ sơ bệnh án điện tử là các phần việc riêng; thanh toán hóa đơn, tải radiograph và treatment plan chi tiết vẫn chưa có API hoàn chỉnh.
