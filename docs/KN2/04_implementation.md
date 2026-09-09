# 04. Implementation

## 1. Document Information
- Project: Dental Management System (DMS)
- Version: 1.0
- Date: 2026-09-08
- Contributors: Nhóm phát triển DMS
- Source documents: `docs/KN2/01_requirements.md`, `docs/KN2/02_design.md`, `docs/KN2/03_implementation_plan.md`
- Repository assessment date: 2026-09-08

## 2. Implementation Summary
Đợt rà soát này ghi nhận trạng thái triển khai thực tế theo thiết kế và kế hoạch đã được phê duyệt. Hiện workspace mới có các thư mục khung `backend/`, `frontend/`, `database/`, `config/` và `ai_services/`; các thư mục này chưa chứa source code, migration, serializer, view hoặc component. `README.md` cũng đang trống. Vì vậy chưa có task code nào có thể đánh dấu Done; các nội dung bên dưới phân biệt rõ artifact đã kiểm tra với artifact cần tạo ở các bước tiếp theo.

Tiến độ code hiện tại: 0% đối với các task triển khai ứng dụng; tài liệu yêu cầu, thiết kế và kế hoạch đã hoàn tất với `STATUS: PASS`.

## 3. Completed Work Items
| Task ID | Description | Owner | Status | Evidence / Reference |
|---|---|---|---|---|
| TASK-001 | Backend setup và cấu hình Django/DRF | Backend | Not started | `backend/` đang trống; chưa có `manage.py`, `requirements.txt` hoặc Django settings. |
| TASK-002 | Frontend setup và design system | Frontend | Not started | `frontend/` đang trống; chưa có `package.json`, `src/` hoặc Tailwind config. |
| TASK-003 | Identity, JWT và RBAC | Backend | Not started | Chưa có User model, JWT settings hoặc permission classes. |
| TASK-004 | Core database models và migrations | Backend | Not started | Chưa có model/migration cho users, patients, allergies, appointments, teeth. |
| TASK-005 | Clinical models và migrations | Backend | Not started | Chưa có treatment plans, prescriptions hoặc prescription items. |
| TASK-006 | Billing, installment, radiograph và audit models | Backend | Not started | Chưa có invoice/payment/media/audit artifact. |
| TASK-007 | Patient Management API | Backend | Not started | Chưa có serializer/view/URL cho `/patients/`. |
| TASK-008 | Appointment Scheduling API | Backend | Not started | Chưa có endpoint, service transaction hoặc conflict validator. |
| TASK-009 | Treatment và Tooth Chart API | Backend | Not started | Chưa có seed 32/20 răng hoặc API tooth condition. |
| TASK-010 | Prescription và allergy check API | Backend | Not started | Chưa có prescription serializer/service và allergy checker. |
| TASK-011 | Billing/payment API | Backend | Not started | Chưa có transaction service cho invoice, installment và payment. |
| TASK-012 | Radiograph, audit và reports API | Backend | Not started | Chưa có upload handler, audit log hoặc report view. |
| TASK-013 | Frontend auth, shell và patient screens | Frontend | Not started | Chưa có React application hoặc route/component files. |
| TASK-014 | Frontend appointment calendar | Frontend | Not started | Chưa có Calendar, AppointmentForm hoặc API integration. |
| TASK-015 | Frontend Tooth Chart | Frontend | Not started | Chưa có `ToothChart`, `Tooth` hoặc `ToothConditionPanel`. |
| TASK-016 | Frontend treatment và prescription | Frontend | Not started | Chưa có TreatmentTimeline, PrescriptionForm hoặc AllergyWarning. |
| TASK-017 | Frontend billing và radiograph | Frontend | Not started | Chưa có invoice/payment form hoặc radiograph uploader. |
| TASK-018 | Integration testing và release hardening | QA | Blocked | Chờ TASK-001 đến TASK-017 tạo được ứng dụng và test targets. |

## 4. Implemented Modules and Features
| Module / Feature | Related Requirement | Implementation Status | Notes |
|---|---|---|---|
| Project scaffolding | REQ-NF-005 | Not started | Có thư mục khung nhưng chưa có Django/React package hoặc cấu hình chạy. |
| Core Models: User, Patient, Allergy, Appointment | REQ-F-001, REQ-F-002, REQ-F-008 | Not started | Artifact dự kiến: `backend/apps/*/models.py`, serializers, migrations và permissions. |
| Tooth Chart 32/20 teeth | REQ-F-003 | Not started | Cần seed 32 mã răng người lớn, 20 mã răng trẻ em và service cập nhật condition. |
| Treatment Plan và Procedure | REQ-F-004 | Not started | Cần model, state transition, API và timeline component. |
| Prescription Allergy Check | REQ-F-005 | Not started | Cần chuẩn hóa tên thuốc, so sánh allergy active và yêu cầu acknowledgement. |
| Billing và Installment Payment | REQ-F-006 | Not started | Cần Decimal calculation và transaction cho invoice/payment/balance. |
| Radiograph Upload | REQ-F-007 | Not started | Cần media storage, MIME/size validation và metadata model. |
| JWT/RBAC/Audit | REQ-F-008, REQ-NF-001 | Not started | Cần xác thực backend, permission matrix và append-only audit log. |

## 5. Configuration and Environment Changes
- Configuration change: Chưa có thay đổi code/config thực tế; cần tạo backend settings, frontend package config, CORS, media và database URL.
- Environment variable: Dự kiến `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DATABASE_URL`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `MEDIA_ROOT`, `MEDIA_URL`; không commit giá trị bí mật.
- Setup note: Dùng SQLite cho local ban đầu; dùng PostgreSQL ở staging/production theo thiết kế. Chỉ chuyển trạng thái Ready sau khi TASK-001 và TASK-002 tạo được ứng dụng chạy được.

## 5.1 Target Directory Structure
```text
dental-clinic-system/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/ (settings, urls, permissions)
│   └── apps/
│       ├── accounts/ (models, serializers, views, permissions)
│       ├── patients/ (models, serializers, services, views, urls)
│       ├── appointments/ (models, serializers, services, views)
│       ├── treatments/ (models, serializers, services, views)
│       ├── prescriptions/ (models, serializers, services, views)
│       ├── billing/ (models, serializers, services, views)
│       ├── radiographs/ (models, serializers, views)
│       └── audit/ (models, services, views)
├── frontend/
│   ├── package.json
│   ├── src/app/ (App, router, auth)
│   ├── src/components/ (layout, common, patients, appointments)
│   ├── src/components/tooth-chart/
│   ├── src/components/treatment/
│   ├── src/components/prescriptions/
│   ├── src/components/billing/
│   ├── src/components/radiographs/
│   ├── src/pages/
│   └── src/services/ (apiClient and feature APIs)
├── database/ (seed data, backup notes, database scripts)
├── config/ (deployment/environment templates)
└── docs/KN2/
```

### 5.2 Actual Versus Target Structure
| Path | Actual state at review | Target artifact |
|---|---|---|
| `backend/` | Directory exists, empty | Django project, apps, models, serializers, views, tests |
| `frontend/` | Directory exists, empty | React/TypeScript app, TailwindCSS, pages/components |
| `database/` | Directory exists, empty | Seed command/data and database operation notes |
| `config/` | Directory exists, empty | Environment/deployment configuration templates |
| `ai_services/` | Directory exists, empty | Not required for current DMS scope; reserve for future use |
| `README.md` | File exists, empty | Setup, migration, seed, run and verify instructions |

## 6. Data and Migration Notes
- Data preparation: Chưa có dữ liệu thật hoặc sample data trong repository. Không đưa dữ liệu bệnh nhân thật vào fixtures hoặc Git.
- Migration step: Chưa có migration file. Sau khi tạo models, chạy `python manage.py makemigrations` rồi `python manage.py migrate`; kiểm tra migration trên database sạch.
- Seed or sample data: Cần tạo management command `seed_dental_data` để tạo roles và 32 mã răng ADULT/20 mã răng CHILD; sample patients chỉ dùng dữ liệu giả.
- Rollback consideration: Mỗi migration phải review trước merge; backup database/media trước staging migration; rollback bằng migration reverse hoặc restore backup, không xóa cứng dữ liệu y tế.

### 6.1 Migration List
| App | Expected migration | Current status |
|---|---|---|
| accounts | User role, permissions | Not created |
| patients | Patient, Allergy | Not created |
| appointments | Appointment and indexes | Not created |
| tooth chart | Tooth, ToothCondition and seed | Not created |
| treatments | TreatmentPlan, TreatmentItem | Not created |
| prescriptions | Prescription, PrescriptionItem | Not created |
| billing | Invoice, InvoiceItem, Installment, Payment | Not created |
| radiographs | Radiograph metadata | Not created |
| audit | Append-only AuditLog | Not created |

## 7. Integration Points
| Integration | Input | Output | Failure Handling |
|---|---|---|---|
| React -> DRF API | JWT, JSON/form-data request | JSON resource/error response | 401 refresh/login; 400 field errors; 403 permission message; retry only safe reads. |
| DRF -> Database | Validated serializer data | Persisted models and transaction result | Atomic rollback on validation or payment failure; log correlation ID. |
| Radiograph -> Media storage | Image file and metadata | File URL plus `Radiograph` record | Reject MIME/size; remove orphan file if DB transaction fails; retry upload. |
| Prescription -> Allergy checker | Patient allergies and medicine names | Warning list and acknowledgement requirement | Block completion until dentist acknowledges an active allergy warning. |
| Billing -> Payment transaction | Invoice, installment and amount | Updated balance/status and payment record | Reject overpayment; rollback all writes; require manager permission for exception. |
| Frontend -> Tooth Chart API | Dentition type, tooth ID, condition | 32/20 tooth state and saved condition | Reject invalid tooth/dentition mapping; show API error without losing selection. |

## 7.1 Serializer and View Inventory
| Feature | Serializers to implement | Views/endpoints to implement | Current status |
|---|---|---|---|
| Auth/RBAC | `TokenSerializer`, `UserSerializer` | `TokenView`, user/role admin views | Not created |
| Patients | `PatientSerializer`, `AllergySerializer` | `PatientViewSet`, allergy actions | Not created |
| Appointments | `AppointmentSerializer` | `AppointmentViewSet`, confirm/cancel actions | Not created |
| Tooth Chart | `ToothSerializer`, `ToothConditionSerializer` | `ToothChartView`, tooth update view | Not created |
| Treatments | `TreatmentPlanSerializer`, `TreatmentItemSerializer` | treatment plan/item views | Not created |
| Prescriptions | `PrescriptionSerializer`, `PrescriptionItemSerializer` | prescription create/list views | Not created |
| Billing | `InvoiceSerializer`, `InvoiceItemSerializer`, `InstallmentSerializer`, `PaymentSerializer` | invoice/installment/payment views | Not created |
| Radiographs | `RadiographSerializer` | multipart upload/list views | Not created |
| Audit/Reports | `AuditLogSerializer`, report serializers | audit and revenue report views | Not created |

## 7.2 Frontend Component Inventory
| Area | Components to implement | Current status |
|---|---|---|
| Shell | `AppShell`, `Sidebar`, `Header`, `ProtectedRoute` | Not created |
| Patients | `PatientForm`, `PatientSummary`, `AllergyList` | Not created |
| Appointments | `Calendar`, `AppointmentForm`, `AppointmentDetail` | Not created |
| Tooth Chart | `ToothChart`, `Tooth`, `ToothConditionPanel` | Not created |
| Treatment | `TreatmentPlanForm`, `TreatmentTimeline` | Not created |
| Prescription | `PrescriptionForm`, `AllergyWarning` | Not created |
| Billing | `InvoiceForm`, `InstallmentSchedule`, `PaymentForm` | Not created |
| Radiographs | `RadiographUploader`, `RadiographGallery` | Not created |

## 8. Known Issues and Limitations
| ID | Description | Impact | Workaround | Status |
|---|---|---|---|---|
| ISSUE-001 | Chưa có source code hoặc package manifest trong các thư mục triển khai. | Không thể chạy server, migrate hoặc test ứng dụng. | Bắt đầu TASK-001/TASK-002 theo `03_implementation_plan.md`. | Open |
| ISSUE-002 | Chưa có migration hoặc seed data. | Không thể verify schema và Tooth Chart 32/20 răng. | Tạo models/migrations rồi chạy seed command trên DB sạch. | Open |
| ISSUE-003 | Chưa chốt giới hạn file X-quang và chính sách trả góp. | Có thể phải điều chỉnh validator và billing service. | Xác nhận với quản lý phòng khám trước khi release. | Open |
| ISSUE-004 | Chưa có test runner hoặc CI configuration. | Chưa thể chứng minh quality gates. | Thiết lập test dependencies và CI trong M-001/M-006. | Open |

## 9. Implementation Verification
- [ ] Build or syntax checks completed: chưa có source code để chạy.
- [ ] Required configuration verified: chưa có package/config files.
- [ ] Main workflows checked: bị chặn bởi TASK-001 đến TASK-017 chưa triển khai.
- [ ] Changes reviewed by the team: tài liệu đã được rà soát theo thiết kế; code review chưa bắt đầu.
- [x] Repository inventory completed: xác nhận các thư mục code hiện trống và README chưa có nội dung.

### 9.1 Planned Verification Commands
Các lệnh sau sẽ dùng sau khi scaffold hoàn tất; hiện chưa chạy thành công vì các file đầu vào chưa tồn tại.

```powershell
# Backend
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py check
python manage.py test

# Database and seed
python manage.py makemigrations
python manage.py migrate
python manage.py seed_dental_data

# Frontend
cd ..\frontend
npm install
npm run build
npm test -- --run
```

### 9.2 Verification Checklist After Implementation
1. Backend `check`, unit/API tests và migrations chạy trên database sạch.
2. Seed tạo đúng 32 răng ADULT và 20 răng CHILD, không trùng code.
3. API kiểm tra 401/403 theo bốn role; appointment chống trùng bác sĩ/phòng.
4. Prescription có allergy warning và bắt buộc acknowledgement khi cần.
5. Billing ghi nhận partial/full payment trong một transaction và tính đúng balance.
6. Frontend build được, route guard hoạt động và các component chính gọi đúng `/api/v1/`.
7. Integration/E2E test hoàn tất luồng bệnh nhân -> lịch -> điều trị -> đơn thuốc -> hóa đơn -> thanh toán.

## 10. Implementation Traceability
| Requirement ID | Implemented Element | Verification Reference |
|---|---|---|
| REQ-F-001 | Planned `Patient` model, serializers, views và Patient screens; chưa có artifact thực tế | TASK-004, TASK-007, TASK-013; blocked pending implementation |
| REQ-F-002 | Planned `Appointment` transaction service, API và Calendar; chưa có artifact thực tế | TASK-004, TASK-008, TASK-014 |
| REQ-F-003 | Planned `Tooth`/`ToothCondition`, seed 32/20 và Tooth Chart components; chưa có artifact thực tế | TASK-009, TASK-015; seed/count test |
| REQ-F-004 | Planned TreatmentPlan/Item models, API và timeline; chưa có artifact thực tế | TASK-005, TASK-009, TASK-016 |
| REQ-F-005 | Planned allergy checker, prescription API và AllergyWarning; chưa có artifact thực tế | TASK-005, TASK-010, TASK-016 |
| REQ-F-006 | Planned invoice/installment/payment models and transaction service; chưa có artifact thực tế | TASK-006, TASK-011, TASK-017 |
| REQ-F-007 | Planned Radiograph metadata, upload API and gallery; chưa có artifact thực tế | TASK-006, TASK-012, TASK-017 |
| REQ-F-008 | Planned JWT/RBAC permission classes and protected routes; chưa có artifact thực tế | TASK-003, TASK-013, TASK-018 |
| REQ-NF-001 | Planned authentication, RBAC, validation and audit log; chưa có artifact thực tế | TASK-003, TASK-012, security test |
| REQ-NF-003 | Planned atomic appointment/payment transactions; chưa có artifact thực tế | TASK-008, TASK-011, integration test |
| REQ-NF-005 | Planned DRF/React separated structure; current directories are empty | TASK-001, TASK-002 |

## 11. Handover Notes
- Pending work: thực hiện TASK-001 đến TASK-018 theo thứ tự dependency; ưu tiên scaffold backend/frontend, models/migrations và test harness.
- Documents to update: README.md sau khi setup chạy được; `04_implementation.md` sau mỗi milestone; `05_review_testing.md` khi có test result.
- Information for reviewers: trạng thái `STATUS: PASS` của tài liệu này xác nhận báo cáo triển khai đã được lập và kiểm tra inventory, không có nghĩa source code đã hoàn thành. Các mục `Not started`, `Blocked` và `Open` cần được giải quyết trước nghiệm thu.

STATUS: PASS
