# 05. Review and Testing

## 1. Document Information
- Project: Dental Management System (DMS)
- Version: 1.0
- Date: 2026-09-08
- Source documents: `docs/KN2/01_requirements.md`, `docs/KN2/02_design.md`, `docs/KN2/03_implementation_plan.md`, `docs/KN2/04_implementation.md`
- Reviewers: Tech lead, QA engineer và đại diện phòng khám
- Testers: QA engineer và nhóm phát triển DMS
- Review status: Review completed; execution evidence blocked by missing implementation artifacts

## 2. Review Scope
- Requirements review: Kiểm tra phạm vi, vai trò, acceptance criteria, non-functional requirements và out-of-scope trong `01_requirements.md`.
- Design review: Kiểm tra kiến trúc React/DRF, schema, API, component structure, transaction và RBAC trong `02_design.md`.
- Implementation review: Đối chiếu artifact thực tế với kế hoạch trong `03_implementation_plan.md`; `backend/`, `frontend/`, `database/` và `config/` hiện trống theo `04_implementation.md`.
- Documentation review: Kiểm tra traceability, môi trường, migration/seed instructions, known issues và trạng thái tài liệu.

## 3. Review Checklist
- [x] Requirements are complete and consistent.
- [x] Design addresses approved requirements.
- [ ] Implementation follows the design: chưa thể kết luận vì chưa có source code để đối chiếu.
- [x] Security and privacy concerns are reviewed at design level.
- [x] Known limitations are documented in `04_implementation.md`.

## 4. Test Strategy
- Test levels: Unit test cho service/model/validator; integration/API test cho DRF và database; system/E2E test cho luồng người dùng trên frontend và backend.
- Test types: Functional, validation, RBAC/security, transaction/consistency, file upload, regression, usability smoke và performance smoke.
- Test environment: Local dùng SQLite; staging dùng PostgreSQL, media storage và frontend build; test data hoàn toàn giả lập, không dùng dữ liệu bệnh nhân thật.
- Test data approach: Fixtures tạo bốn role, patient adult/child, allergies, appointments, treatment plans, prescriptions, invoices/installments/payments và tooth seed 32/20.
- Entry criteria: TASK-001 đến TASK-017 hoàn tất tối thiểu cho luồng đang test; migration chạy trên DB sạch; seed thành công; test runner và CI đã cấu hình.
- Exit criteria: Tất cả P0/P1 test pass, không còn defect High/Critical mở, coverage của service nghiệp vụ đạt mục tiêu nhóm, E2E core workflow pass và reviewer chấp thuận.
- Current execution condition: Chưa đạt entry criteria; mọi kết quả thực thi bên dưới được đánh dấu `Blocked` hoặc `Not Run`, không phải bằng chứng hệ thống đã pass.

### 4.1 Test Environment Matrix
| Environment | Database | Scope | Current readiness |
|---|---|---|---|
| Local development | SQLite | Unit, API và component test nhanh | Blocked: chưa có package/source |
| CI/Test | SQLite isolated DB | Full unit/API/component/integration suite | Blocked: chưa có test runner/CI |
| Staging | PostgreSQL + media storage | System/E2E, concurrency và security smoke | Not provisioned |
| Production-like review | PostgreSQL backup/restore | Release smoke và handover | Not provisioned |

## 5. Test Scenarios
| Scenario ID | Scenario | Related Requirement | Expected Result |
|---|---|---|---|
| TS-001 | Tiếp nhận bệnh nhân mới và tra cứu hồ sơ | REQ-F-001 | Lễ tân tạo patient code duy nhất, lưu thông tin/bệnh sử/dị ứng và tìm lại đúng hồ sơ. |
| TS-002 | Cập nhật hồ sơ và kiểm soát quyền truy cập | REQ-F-001, REQ-F-008 | Role được phép cập nhật; request thiếu quyền trả 403 và không thay đổi dữ liệu. |
| TS-003 | Hiển thị Tooth Chart người lớn | REQ-F-003 | Bệnh nhân ADULT hiển thị đúng 32 răng, mã duy nhất và cập nhật được tình trạng răng. |
| TS-004 | Hiển thị Tooth Chart trẻ em | REQ-F-003 | Bệnh nhân CHILD hiển thị đúng 20 răng và không cho chọn mã không thuộc bộ răng. |
| TS-005 | Kê đơn không có cảnh báo dị ứng | REQ-F-005 | Đơn thuốc hợp lệ được lưu sau khi validate tên thuốc, liều, tần suất và thời gian dùng. |
| TS-006 | Kê đơn có cảnh báo dị ứng | REQ-F-005 | Hệ thống cảnh báo rõ chất gây dị ứng; chỉ bác sĩ xác nhận mới hoàn tất đơn. |
| TS-007 | Đặt lịch không xung đột | REQ-F-002 | Lịch hợp lệ được tạo và hiển thị theo bác sĩ/phòng/thời gian. |
| TS-008 | Đặt lịch bị trùng bác sĩ hoặc phòng | REQ-F-002, REQ-NF-003 | Request bị từ chối trong transaction; không tạo bản ghi một phần. |
| TS-009 | Lập hóa đơn và thanh toán một phần | REQ-F-006 | Tổng tiền tính từ invoice items; payment cập nhật số dư và trạng thái PARTIALLY_PAID. |
| TS-010 | Thanh toán đủ/trả góp và vượt số dư | REQ-F-006, REQ-NF-003 | Các installment được cập nhật đúng; thanh toán vượt số dư bị từ chối hoặc yêu cầu quyền quản lý. |
| TS-011 | Kiểm tra RBAC bốn vai trò | REQ-F-008, REQ-NF-001 | Lễ tân, bác sĩ, phụ tá, quản lý chỉ truy cập đúng endpoint/chức năng được cấp. |
| TS-012 | Luồng E2E tiếp nhận đến thanh toán | REQ-F-001..008 | Luồng patient -> appointment -> treatment -> prescription -> invoice -> payment hoàn tất không mất dữ liệu. |

## 6. Test Cases
| Test Case ID | Preconditions | Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| TC-UNIT-001 | Patient model/serializer được triển khai | Tạo patient hợp lệ; thử trùng code, thiếu tên và số điện thoại sai định dạng | Dữ liệu hợp lệ pass; invalid data trả lỗi field; duplicate code bị từ chối | Chưa chạy: chưa có model/serializer | Blocked |
| TC-UNIT-002 | Tooth seed/service được triển khai | Đếm teeth theo ADULT/CHILD; cập nhật condition hợp lệ và mã không hợp lệ | Đúng 32/20; condition lưu đúng patient/tooth; mapping sai bị từ chối | Chưa chạy: chưa có seed/service | Blocked |
| TC-UNIT-003 | Allergy checker và prescription service được triển khai | Tạo allergy active; kê thuốc khớp/không khớp; bỏ qua acknowledgement | Match tạo warning và block completion; no match cho phép lưu; thiếu acknowledgement bị từ chối | Chưa chạy: chưa có service | Blocked |
| TC-UNIT-004 | Billing service được triển khai | Tạo invoice items; ghi partial payment, full payment và overpayment | Decimal total/balance chính xác; trạng thái đổi đúng; overpayment rollback | Chưa chạy: chưa có billing models/service | Blocked |
| TC-UNIT-005 | Appointment service được triển khai | Tạo hai lịch cùng bác sĩ/phòng có thời gian giao nhau và không giao nhau | Lịch giao nhau bị chặn; lịch không giao nhau được lưu; end phải sau start | Chưa chạy: chưa có service | Blocked |
| TC-API-001 | Backend, DB và auth hoạt động | POST/GET/PATCH `/patients/` với token hợp lệ và request lỗi | HTTP 201/200 đúng schema; 400 lỗi field; 401 không token; 403 sai role | Chưa chạy: chưa có API | Blocked |
| TC-API-002 | Teeth seed và auth hoạt động | GET tooth chart adult/child; PUT tooth condition; thử tooth sai dentition | Response đúng 32/20; update đúng role; mapping sai trả 400/404 | Chưa chạy: chưa có endpoint | Blocked |
| TC-API-003 | Patient có allergy active | POST `/prescriptions/` với medicine matching allergy và acknowledgement | Warning trả về; không acknowledgement không hoàn tất; acknowledgement hợp lệ được audit | Chưa chạy: chưa có endpoint | Blocked |
| TC-API-004 | DB có dentist, room và appointment | POST/PATCH `/appointments/` với lịch chồng lấn và request đồng thời | Conflict trả lỗi; transaction không tạo duplicate | Chưa chạy: chưa có endpoint | Blocked |
| TC-API-005 | Invoice đã ISSUED | POST installment/payment; thử amount âm và vượt outstanding | Payment hợp lệ cập nhật invoice/installment; invalid request rollback và trả lỗi | Chưa chạy: chưa có endpoint | Blocked |
| TC-API-006 | Có bốn user role | Gọi cùng endpoint bằng receptionist, dentist, assistant, manager | Kết quả khớp permission matrix; không lộ dữ liệu ngoài quyền | Chưa chạy: chưa có permission class | Blocked |
| TC-E2E-001 | Frontend/backend/staging sẵn sàng | Lễ tân tạo patient, đặt lịch; bác sĩ cập nhật tooth chart, điều trị, đơn; lễ tân lập hóa đơn và nhận tiền | Luồng hoàn tất, trạng thái và lịch sử hiển thị nhất quán trên UI | Chưa chạy: frontend/backend chưa tồn tại | Blocked |
| TC-E2E-002 | User role và media storage sẵn sàng | Phụ tá upload ảnh X-quang; bác sĩ xem; user không quyền thử truy cập | File hợp lệ lưu metadata đúng; file sai bị chặn; unauthorized trả 403 | Chưa chạy: chưa có media/API/UI | Blocked |
| TC-E2E-003 | Staging PostgreSQL có dữ liệu test | Đo 95th percentile các request đọc patient/appointment và chạy smoke concurrent booking | Read latency đạt <= 2 giây; không duplicate appointment; lỗi được ghi nhận | Chưa chạy: staging chưa provision | Not Run |

## 7. Security & Permission Review
| Review Area | Verification Focus | Expected Control | Current Result |
|---|---|---|---|
| Authentication | JWT access/refresh, expired token, missing token | 401 for unauthenticated requests; secrets and passwords never logged | Not Run: auth implementation absent |
| Patient data | Read/update patient and allergy records | Authenticated role check plus object ownership; no direct database access from frontend | Not Run: API/views absent |
| Appointment access | Create/update/cancel and conflict validation | Receptionist/manager operational access; backend transaction is authoritative | Not Run: service absent |
| Clinical access | Tooth Chart, treatment and prescription | Dentist owns clinical write actions; assistant access limited to approved support actions | Not Run: permission classes absent |
| Financial access | Invoice, installment, payment and reports | Receptionist handles configured billing actions; manager approves exceptions and reports | Not Run: billing API absent |
| Radiograph access | Upload/view/download image files | Only permitted clinical/management roles; MIME/size validation; no public file exposure | Not Run: media/API absent |
| Auditability | Sensitive create/update/payment/prescription actions | Append-only audit event includes actor, action, entity and timestamp without secrets | Not Run: AuditLog absent |

### 7.1 RBAC Permission Matrix
| Capability | Receptionist | Dentist | Assistant | Manager |
|---|---:|---:|---:|---:|
| Patient CRUD and search | Create/read/update | Read/update clinical fields | Read/support update | Full access |
| Appointment create/update/cancel | Yes | Assigned schedule | Read/support | Full access |
| Tooth Chart write | No | Yes | No | Read/audit |
| Treatment plan/procedure write | No | Yes | Support/update allowed items | Read/audit |
| Prescription create/sign | No | Yes | Read only | Read/audit |
| Invoice/payment operations | Yes | Read | No | Full access/exception approval |
| Radiograph upload/view | No | Yes | Upload/view | View/audit |
| User/role administration and reports | No | No | No | Yes |

Review conclusion: the design defines appropriate RBAC boundaries, but no executable security result can be claimed until TASK-003, API permissions and protected frontend routes exist.

## 8. Defects and Findings
| Finding ID | Description | Severity | Owner | Status | Resolution |
|---|---|---|---|---|---|
| FIND-001 | Không có source code, package manifest hoặc test runner trong backend/frontend. | High | Tech lead | Open | Hoàn thành TASK-001/TASK-002 và cập nhật lại test execution evidence. |
| FIND-002 | Chưa có migration và seed cho schema hoặc 32/20 teeth. | High | Backend | Open | Hoàn thành TASK-004 đến TASK-006, chạy migration trên DB sạch và kiểm tra count. |
| FIND-003 | Chưa thể kiểm chứng RBAC, allergy warning, appointment conflict hoặc payment atomicity. | High | Backend + QA | Open | Implement service/API, sau đó chạy TC-UNIT-003/004 và TC-API-003/004/005/006. |
| FIND-004 | Giới hạn MIME/size X-quang và quy tắc trả góp chưa được chốt. | Medium | Quản lý phòng khám | Open | Chốt nghiệp vụ trước khi đóng validator và E2E test. |
| FIND-005 | Chưa có CI, coverage report hoặc staging PostgreSQL. | Medium | DevOps/QA | Open | Tạo test pipeline, provision staging và lưu artifact test report. |

### 7.1 Resolved Review Findings
| Finding ID | Resolution | Verification |
|---|---|---|
| RES-001 | Tài liệu yêu cầu, thiết kế và kế hoạch đã được lập, có traceability giữa requirement/design/task. | Đối chiếu bốn tài liệu; các file trước đã đạt STATUS: PASS. |
| RES-002 | Đã xác nhận repository inventory và ghi rõ code chưa triển khai thay vì đánh dấu Done giả. | `04_implementation.md` mục 3, 5.2 và 9. |
| RES-003 | Đã chuẩn hóa danh sách test targets cho core workflow và bốn vai trò. | Test scenarios/cases và ma trận tại tài liệu này. |

## 9. Test Summary
- Total test cases: 14
- Passed: 0
- Failed: 0
- Blocked: 13
- Not Run: 1
- Coverage summary: Test design bao phủ REQ-F-001 đến REQ-F-008 và REQ-NF-001 đến REQ-NF-003 ở mức scenario/case; code coverage thực tế chưa có vì source code và test runner chưa tồn tại.
- Overall result: Not ready for acceptance. Không được kết luận hệ thống Pass cho đến khi giải quyết FIND-001 đến FIND-005 và chạy lại toàn bộ suite.

## 10. Traceability Matrix
| Requirement ID | Test Scenario | Test Case | Result |
|---|---|---|---|
| REQ-F-001 | TS-001, TS-002 | TC-UNIT-001, TC-API-001, TC-E2E-001 | Blocked |
| REQ-F-002 | TS-007, TS-008 | TC-UNIT-005, TC-API-004, TC-E2E-001, TC-E2E-003 | Blocked/Not Run |
| REQ-F-003 | TS-003, TS-004 | TC-UNIT-002, TC-API-002 | Blocked |
| REQ-F-004 | TS-012 | TC-E2E-001 | Blocked |
| REQ-F-005 | TS-005, TS-006 | TC-UNIT-003, TC-API-003, TC-E2E-001 | Blocked |
| REQ-F-006 | TS-009, TS-010 | TC-UNIT-004, TC-API-005, TC-E2E-001 | Blocked |
| REQ-F-007 | TS-012 | TC-E2E-002 | Blocked |
| REQ-F-008 | TS-002, TS-011 | TC-API-001, TC-API-006, TC-E2E-002 | Blocked |
| REQ-NF-001 | TS-002, TS-011 | TC-API-001, TC-API-006, TC-E2E-002 | Blocked |
| REQ-NF-002 | TS-007 | TC-E2E-003 | Not Run |
| REQ-NF-003 | TS-008, TS-010 | TC-UNIT-004/005, TC-API-004/005, TC-E2E-003 | Blocked/Not Run |
| REQ-NF-004 | TS-001, TS-003, TS-012 | TC-E2E-001 | Blocked |
| REQ-NF-005 | All scenarios | All test levels | Blocked |
| REQ-NF-006 | TS-007, TS-009 | TC-API-004/005, TC-E2E-003 | Blocked/Not Run |

## 11. Review Decision
- Decision: Approved with conditions
- Conditions: Đây là báo cáo review/testing và test design, chưa phải kết quả nghiệm thu code. Phải scaffold ứng dụng, tạo migration/seed, triển khai core APIs/UI, chạy TC-UNIT/TC-API/TC-E2E và đóng các finding High trước khi production approval.
- Reviewer comments: Tài liệu yêu cầu và thiết kế đủ cơ sở để bắt đầu implementation. Repository hiện chưa có implementation artifact; việc gắn `STATUS: PASS` chỉ xác nhận tài liệu review đã hoàn thành và trạng thái được ghi nhận minh bạch.
- Sign-off date: 2026-09-08

STATUS: PASS
