-- SQLite schema for the 13 Django clinic application tables.
-- Requires Django auth tables first: python manage.py migrate auth contenttypes
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS "clinic_appointment" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "dentist_name" varchar(160) NOT NULL, "room" varchar(40) NOT NULL, "start_at" datetime NOT NULL, "end_at" datetime NOT NULL, "status" varchar(20) NOT NULL, "notes" text NOT NULL, "patient_id" bigint NOT NULL REFERENCES "clinic_patient" ("id") DEFERRABLE INITIALLY DEFERRED, "doctor_id" bigint NULL REFERENCES "clinic_doctor" ("id") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "appointment_end_after_start" CHECK ("end_at" > ("start_at")));

CREATE TABLE IF NOT EXISTS "clinic_clinicuser" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "phone" varchar(30) NOT NULL, "created_at" datetime NOT NULL, "user_id" integer NOT NULL UNIQUE REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "role_id" bigint NOT NULL REFERENCES "clinic_role" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE TABLE IF NOT EXISTS "clinic_doctor" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "license_number" varchar(40) NOT NULL UNIQUE, "specialization" varchar(120) NOT NULL, "clinic_user_id" bigint NOT NULL UNIQUE REFERENCES "clinic_clinicuser" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE TABLE IF NOT EXISTS "clinic_invoice" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "invoice_number" varchar(30) NOT NULL UNIQUE, "total_amount" decimal NOT NULL, "paid_amount" decimal NOT NULL, "status" varchar(20) NOT NULL, "issued_at" datetime NOT NULL, "patient_id" bigint NOT NULL REFERENCES "clinic_patient" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE TABLE IF NOT EXISTS "clinic_invoiceitem" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "description" varchar(180) NOT NULL, "quantity" smallint unsigned NOT NULL CHECK ("quantity" >= 0), "unit_price" decimal NOT NULL, "amount" decimal NOT NULL, "invoice_id" bigint NOT NULL REFERENCES "clinic_invoice" ("id") DEFERRABLE INITIALLY DEFERRED, "service_id" bigint NULL REFERENCES "clinic_service" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE TABLE IF NOT EXISTS "clinic_patient" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "patient_code" varchar(20) NOT NULL UNIQUE, "full_name" varchar(160) NOT NULL, "phone" varchar(30) NOT NULL, "date_of_birth" date NULL, "dentition_type" varchar(10) NOT NULL, "medical_history" text NOT NULL, "allergies" text NOT NULL, "created_at" datetime NOT NULL);

CREATE TABLE IF NOT EXISTS "clinic_payment" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "amount" decimal NOT NULL, "method" varchar(20) NOT NULL, "paid_at" datetime NOT NULL, "invoice_id" bigint NOT NULL REFERENCES "clinic_invoice" ("id") DEFERRABLE INITIALLY DEFERRED, "received_by_id" bigint NULL REFERENCES "clinic_clinicuser" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE TABLE IF NOT EXISTS "clinic_role" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "code" varchar(30) NOT NULL UNIQUE, "name" varchar(80) NOT NULL, "description" text NOT NULL);

CREATE TABLE IF NOT EXISTS "clinic_service" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "code" varchar(30) NOT NULL UNIQUE, "name" varchar(160) NOT NULL, "description" text NOT NULL, "price" decimal NOT NULL, "duration_minutes" smallint unsigned NOT NULL CHECK ("duration_minutes" >= 0), "is_active" bool NOT NULL);

CREATE TABLE IF NOT EXISTS "clinic_tooth" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "code" varchar(4) NOT NULL, "dentition_type" varchar(10) NOT NULL, "display_order" smallint unsigned NOT NULL CHECK ("display_order" >= 0), CONSTRAINT "unique_tooth_code_type" UNIQUE ("code", "dentition_type"));

CREATE TABLE IF NOT EXISTS "clinic_toothcondition" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "condition" varchar(120) NOT NULL, "note" text NOT NULL, "updated_at" datetime NOT NULL, "patient_id" bigint NOT NULL REFERENCES "clinic_patient" ("id") DEFERRABLE INITIALLY DEFERRED, "tooth_id" bigint NOT NULL REFERENCES "clinic_tooth" ("id") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "unique_patient_tooth" UNIQUE ("patient_id", "tooth_id"));

CREATE TABLE IF NOT EXISTS "clinic_treatmentitem" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "procedure_name" varchar(180) NOT NULL, "cost" decimal NOT NULL, "status" varchar(20) NOT NULL, "appointment_id" bigint NULL REFERENCES "clinic_appointment" ("id") DEFERRABLE INITIALLY DEFERRED, "service_id" bigint NULL REFERENCES "clinic_service" ("id") DEFERRABLE INITIALLY DEFERRED, "tooth_id" bigint NULL REFERENCES "clinic_tooth" ("id") DEFERRABLE INITIALLY DEFERRED, "plan_id" bigint NOT NULL REFERENCES "clinic_treatmentplan" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE TABLE IF NOT EXISTS "clinic_treatmentplan" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(180) NOT NULL, "status" varchar(20) NOT NULL, "start_date" date NULL, "end_date" date NULL, "created_at" datetime NOT NULL, "dentist_id" bigint NOT NULL REFERENCES "clinic_doctor" ("id") DEFERRABLE INITIALLY DEFERRED, "patient_id" bigint NOT NULL REFERENCES "clinic_patient" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE INDEX IF NOT EXISTS "clinic_appointment_doctor_id_a005cb8d" ON "clinic_appointment" ("doctor_id");

CREATE INDEX IF NOT EXISTS "clinic_appointment_patient_id_dd04daf6" ON "clinic_appointment" ("patient_id");

CREATE INDEX IF NOT EXISTS "clinic_clinicuser_role_id_d8415830" ON "clinic_clinicuser" ("role_id");

CREATE INDEX IF NOT EXISTS "clinic_invoice_patient_id_0aaab73a" ON "clinic_invoice" ("patient_id");

CREATE INDEX IF NOT EXISTS "clinic_invoiceitem_invoice_id_1ea37174" ON "clinic_invoiceitem" ("invoice_id");

CREATE INDEX IF NOT EXISTS "clinic_invoiceitem_service_id_521c7164" ON "clinic_invoiceitem" ("service_id");

CREATE INDEX IF NOT EXISTS "clinic_payment_invoice_id_eb3afba9" ON "clinic_payment" ("invoice_id");

CREATE INDEX IF NOT EXISTS "clinic_payment_received_by_id_0e5962a4" ON "clinic_payment" ("received_by_id");

CREATE INDEX IF NOT EXISTS "clinic_toothcondition_patient_id_d5f40644" ON "clinic_toothcondition" ("patient_id");

CREATE INDEX IF NOT EXISTS "clinic_toothcondition_tooth_id_2c510a4d" ON "clinic_toothcondition" ("tooth_id");

CREATE INDEX IF NOT EXISTS "clinic_treatmentitem_appointment_id_0154423b" ON "clinic_treatmentitem" ("appointment_id");

CREATE INDEX IF NOT EXISTS "clinic_treatmentitem_plan_id_9f433e47" ON "clinic_treatmentitem" ("plan_id");

CREATE INDEX IF NOT EXISTS "clinic_treatmentitem_service_id_b4e3fba3" ON "clinic_treatmentitem" ("service_id");

CREATE INDEX IF NOT EXISTS "clinic_treatmentitem_tooth_id_4efe875e" ON "clinic_treatmentitem" ("tooth_id");

CREATE INDEX IF NOT EXISTS "clinic_treatmentplan_dentist_id_ed2af775" ON "clinic_treatmentplan" ("dentist_id");

CREATE INDEX IF NOT EXISTS "clinic_treatmentplan_patient_id_33fefe99" ON "clinic_treatmentplan" ("patient_id");
