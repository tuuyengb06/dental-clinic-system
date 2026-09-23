# 06. Final Delivery

## 1. Document Information
- Project: Dental Management System (DMS)
- Version: 1.0 documentation baseline
- Delivery date: 2026-09-08
- Delivery owner: Nhóm phát triển DMS
- Approvers: Quản lý phòng khám, Tech lead và QA engineer
- Source documents: `docs/KN2/01_requirements.md` đến `docs/KN2/05_review_testing.md`

## 2. Delivery Summary
Bộ tài liệu KN2 đã hoàn tất từ yêu cầu, thiết kế, kế hoạch triển khai, ghi nhận implementation đến review/testing. Baseline mô tả đầy đủ hệ thống DMS gồm quản lý bệnh nhân, lịch hẹn, Tooth Chart 32/20 răng, kế hoạch điều trị, kê đơn và cảnh báo dị ứng, hóa đơn/trả góp, upload X-quang, JWT/RBAC và audit.

Tuy nhiên, theo kiểm tra thực tế ở `04_implementation.md`, các thư mục `backend/`, `frontend/`, `database/` và `config/` chưa có source code, package manifest, migration hoặc test runner. Vì vậy lần bàn giao này là bàn giao tài liệu và baseline triển khai, chưa phải release runtime để đưa vào vận hành. `STATUS: PASS` ở cuối tài liệu xác nhận báo cáo bàn giao đã được lập và kiểm tra, không thay thế điều kiện nghiệm thu code.

## 3. Delivered Items
| Item | Description | Version / Location | Status |
|---|---|---|---|
| Requirements baseline | Phạm vi, vai trò, functional/non-functional requirements và out-of-scope | `docs/KN2/01_requirements.md` | Complete |
| Architecture and database design | Kiến trúc React/DRF, schema, API, components, security và transaction rules | `docs/KN2/02_design.md` | Complete |
| Implementation plan | 6 milestone, 18 task, priority, dependency và test plan | `docs/KN2/03_implementation_plan.md` | Complete |
| Implementation status report | Inventory thực tế, target structure, migration/serializer/view/component inventory và setup commands | `docs/KN2/04_implementation.md` | Complete; code pending |
| Review and testing report | Strategy, 14 test cases, traceability, security/RBAC review và findings | `docs/KN2/05_review_testing.md` | Complete; execution blocked |
| Backend runtime | Django REST Framework application, models, APIs, migrations | `backend/` | Pending |
| Frontend runtime | React + TailwindCSS application and screens | `frontend/` | Pending |
| Database and seed | PostgreSQL/SQLite schema, migrations và seed 32/20 teeth | `database/` and Django apps | Pending |

## 4. Final Feature Checklist
- [x] Approved requirements delivered as a reviewed requirements baseline.
- [x] Designed components delivered as an approved architecture/design baseline.
- [ ] Required implementation completed: 18 code tasks remain Not started/Blocked.
- [x] Review completed at documentation and repository-inventory level.
- [ ] Testing completed: test design is complete, but execution is blocked; 13 cases Blocked and 1 Not Run.
- [ ] User documentation completed: setup instructions are drafted; operational guide requires a runnable deployment.

### 4.1 Core Feature Delivery Status
| Core feature | Intended delivery | Current delivery status | Release condition |
|---|---|---|---|
| Patient Management | CRUD/search hồ sơ, bệnh sử, dị ứng, lịch sử | Not implemented | Patient models, serializers, views, UI và API tests pass |
| Tooth Chart 32/20 | 32 răng người lớn, 20 răng trẻ em, cập nhật condition | Not implemented | Seed/count tests và frontend component tests pass |
| Appointment | Calendar, confirm/cancel, chống trùng bác sĩ/phòng | Not implemented | Transaction/concurrency API tests pass |
| Prescription/Allergy | Kê đơn, allergy warning, acknowledgement | Not implemented | Allergy unit/API/E2E tests pass |
| Billing/Installment | Invoice, payment nhiều lần, balance và installment | Not implemented | Atomic payment/rollback tests pass |
| Radiograph | Upload metadata, media storage và phân quyền xem | Not implemented | MIME/size/security and upload E2E tests pass |

## 5. Validation and Acceptance
| Acceptance Item | Evidence | Result | Accepted By |
|---|---|---|---|
| Requirements completeness | `01_requirements.md`, STATUS: PASS | Pass for documentation baseline | Review team |
| Design consistency | `02_design.md`, STATUS: PASS | Pass for design baseline | Tech lead |
| Implementation inventory | `04_implementation.md`, repository directories checked | Pass as status report; runtime not delivered | Tech lead |
| Functional test design | `05_review_testing.md`, 14 test cases and traceability matrix | Pass as test plan; execution blocked | QA engineer |
| Backend/frontend build | No `manage.py`, `package.json` or source artifacts present | Not accepted | QA engineer |
| Core workflow E2E | TC-E2E-001 through TC-E2E-003 | Not accepted; blocked/not run | QA engineer |
| Production readiness | Open High findings FIND-001 to FIND-003 | Not ready | Quản lý phòng khám |

### 5.1 Acceptance Decision
Decision: Approved with conditions for documentation handover only. Production acceptance is deferred until implementation tasks are completed, test entry criteria are met, all P0/P1 tests pass and High findings are closed.

## 6. Deployment or Handover Instructions
- Prerequisites: Python và virtual environment; Node.js/npm; SQLite cho local hoặc PostgreSQL cho staging/production; media storage; Git. Không dùng dữ liệu bệnh nhân thật trong local/test.
- Setup steps:
	1. Scaffold backend Django/DRF và frontend React theo target structure trong `04_implementation.md`.
	2. Tạo file environment từ template, đặt `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DATABASE_URL`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `MEDIA_ROOT` và `MEDIA_URL`.
	3. Backend: `cd backend`; tạo/activate venv; `pip install -r requirements.txt`.
	4. Frontend: `cd frontend`; chạy `npm install`.
	5. Tạo schema bằng `python manage.py makemigrations` và `python manage.py migrate`.
	6. Chạy `python manage.py seed_dental_data`; xác nhận 32 mã ADULT và 20 mã CHILD.
- Start or usage steps:
	1. Backend: `python manage.py check` rồi `python manage.py runserver`.
	2. Frontend: `npm run dev` hoặc lệnh start trong `package.json`.
	3. Đăng nhập bằng test users theo role; kiểm tra patient, appointment, Tooth Chart, prescription, invoice/payment và radiograph workflow.
	4. Chạy `python manage.py test`, frontend test/build và bộ E2E trước khi bàn giao staging.
- Configuration notes: Local ưu tiên SQLite; staging/production dùng PostgreSQL. Bật HTTPS, backup database/media, không commit secrets, giới hạn upload X-quang và cấu hình CORS theo domain thật.
- Rollback steps: Dừng release; backup database/media hiện tại; reverse migration đã review hoặc restore backup; khôi phục bản build trước; kiểm tra patient/appointment/payment integrity rồi ghi nhận incident.

### 6.1 Handover Checklist
- [ ] Repository có backend/frontend source và lockfiles.
- [ ] Migrations chạy thành công trên database sạch và staging.
- [ ] Seed tạo đủ roles, sample data giả và 32/20 teeth.
- [ ] Environment secrets được cấp ngoài source control.
- [ ] CI chạy unit/API/component/integration test.
- [ ] Staging E2E pass cho bốn vai trò và core workflow.
- [ ] Backup/restore drill và rollback được diễn tập.

## 7. Known Limitations and Follow-up Work
| ID | Limitation / Follow-up | Priority | Owner | Target Date |
|---|---|---|---|---|
| FOLLOWUP-001 | Scaffold Django/DRF backend, React frontend, dependency manifests và CI test runner. | High | Tech lead | Before release |
| FOLLOWUP-002 | Implement models/migrations/seed cho toàn bộ schema và 32/20 teeth. | High | Backend | Before M-002 exit |
| FOLLOWUP-003 | Implement JWT/RBAC, Patient, Appointment, Treatment, Prescription, Billing và Radiograph APIs. | High | Backend | Before M-004 exit |
| FOLLOWUP-004 | Implement frontend screens, Tooth Chart, allergy warning, billing/installment và upload gallery. | High | Frontend | Before M-005 exit |
| FOLLOWUP-005 | Chốt MIME/size X-quang và chính sách trả góp với phòng khám. | Medium | Quản lý phòng khám | Before UAT |
| FOLLOWUP-006 | Chạy 14 test cases, đo performance <= 2 giây p95 và đóng FIND-001 đến FIND-005. | High | QA + DevOps | Before production approval |
| FOLLOWUP-007 | Bổ sung README vận hành, backup/restore, monitoring và incident runbook. | Medium | DevOps | Before handover |

## 8. Support and Maintenance
- Support contact: Tech lead làm đầu mối kỹ thuật; quản lý phòng khám làm đầu mối nghiệp vụ.
- Issue reporting process: Tạo issue với severity, môi trường, role, bước tái hiện, expected/actual result, log không chứa PII và liên kết test case/requirement.
- Maintenance schedule: Review dependency và security hàng tháng; backup database/media hàng ngày; kiểm tra restore hàng quý; rà soát audit log và quyền user hàng tháng.
- Backup and recovery owner: DevOps/Quản lý hệ thống; lưu database backup và media backup tách biệt, mã hóa và kiểm tra khả năng phục hồi.
- Operational checks: health endpoint, disk/media capacity, failed login/payment/upload logs, pending installments, overdue invoices và database migration status.

## 9. Final Approval
- Prepared by: Nhóm phát triển DMS
- Reviewed by: Tech lead, QA engineer và đại diện phòng khám
- Approved by: TBD - chờ nghiệm thu runtime
- Approval date: TBD

## 10. Delivery Notes
Đã thống nhất sử dụng Django REST Framework + React/TailwindCSS, PostgreSQL cho staging/production và SQLite cho local. Out of scope gồm kho vật tư tiêu hao, tích hợp trực tiếp phần cứng X-quang và bảo hiểm y tế nhà nước. Không được gọi hệ thống là production-ready chỉ dựa trên trạng thái PASS của tài liệu; cần cập nhật báo cáo này sau khi code và test runtime hoàn tất.

STATUS: PASS
