# SKYLINK GROUP OF COMPANIES — Corporate Web Platform

[![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django)](https://www.djangoproject.com/)
[![Database](https://img.shields.io/badge/Database-MySQL_8.x-00758F?logo=mysql)](https://www.mysql.com/)
[![Tailwind CSS](https://img.shields.io/badge/CSS-Tailwind_CSS-38B2AC?logo=tailwind-css)](https://tailwindcss.com/)
[![Status](https://img.shields.io/badge/Tests-12%20Passed-10B981)](#automated-testing)

A production-ready corporate web application and lead operations pipeline built for **SKYLINK GROUP OF COMPANIES**, inspired by modern corporate portals (e.g. DSS HR) with bespoke branding, normalized relational schema, functional public forms, email alerts, secure resume uploads, and an internal administration dashboard.

---

## 🏢 Corporate Structure & Verified Entity

| Detail | Official Verified Record |
|---|---|
| **Holding Entity** | **Skylink Staffing Solutions Pvt. Ltd.** |
| **Corporate Identity (CIN)** | `U78300BR2025PTC075220` |
| **Managing Director** | **Er. Mahtab Alam (Guddu)** |
| **Headquarters** | Skylink Tower Turkha, Nahar Road, Near Bypass Road, Gopalganj, Bihar - 841428 |
| **Branch / Operational** | Turkaha, Thawe Road, Near Masjid, Gopalganj, Bihar - 841428 |
| **Corporate Helpline** | `+91 90455 85073` &nbsp;|&nbsp; `+91 61564 50214` |
| **Official Email** | `skylinktravels73@gmail.com` |
| **Web Domain** | `skylinkstaffingsolutions.com` |
| **Motto** | *"Your Growth, Our Commitment"* |
| **Core Values** | Service • Security • Satisfaction |

---

## 🌐 The Three Business Divisions

1. **Skylink Staffing Solutions Pvt. Ltd.** (`/staffing/`)
   - International (Gulf/Middle East) & Pan-India recruitment
   - Skilled & unskilled workforce supply
   - HR solutions, payroll, and statutory consulting
   - Trade testing & pre-departure GAMCA/visa documentation
   - Forms: [Employer Manpower Requisition](/staffing/employer-enquiry/) & [Candidate Job Application](/staffing/careers/)

2. **Skylink Skill Academy** (`/skill-academy/`)
   - Technical vocational training programs with practical labs
   - Trades: Electrician, AC & Refrigeration, Plumbing, and HSE Industrial Safety
   - Flexible batches: Morning, Afternoon, Evening & Weekend
   - Form: [Course Admission Form](/skill-academy/course-admission/)

3. **Skylink Maintenance Services** (`/maintenance/`)
   - Turnkey property maintenance: Residential, Commercial, and Institutional
   - 24/7 technician dispatch for Electrical, HVAC, Plumbing, and Handyman repairs
   - Annual Maintenance Contracts (AMC)
   - Form: [Service Request Booking](/maintenance/service-request/)

---

## 💻 Technology Architecture

- **Backend:** Python 3.12 + Django 5.2
- **Database:** MySQL 8.x (via `PyMySQL` + Django ORM) with UTF8MB4 charset
- **Frontend:** Django Templates + HTML5 + Tailwind CSS + Vanilla JS
- **Static Assets:** Whitenoise compression with cache-busting manifest
- **Email Delivery:** Transactional SMTP (Gmail / Resend relay)
- **File Storage:** Private media upload directories for resumes and photos with size/type validation
- **Security:** Django CSRF tokens, Honeypot spam shields, XSS escaping, SQL injection protection via ORM, and role-based staff authorization

---

## 🗄️ Normalized MySQL Database Schema

```
                  ┌──────────────────────────────────────────────┐
                  │                 Submission                   │
                  │ (UUID PK, Ref #, Division, Type, Status,     │
                  │  Contact Info, Message, Assigned To, Dates)  │
                  └──────────────────────┬───────────────────────┘
                                         │ 1:1
     ┌───────────────────┬───────────────┴───────────────┬───────────────────┐
     │ 1:1               │ 1:1                           │ 1:1               │ 1:1
┌────┴────────────┐ ┌────┴───────────┐ ┌─────────────────┴─┐ ┌───────────────┴───┐
│  CandidateApp   │ │  EmployerEnq   │ │  CourseAdmission  │ │  MaintenanceReq   │
│ (Role, Exp,     │ │ (Industry,     │ │ (Course, Batch,   │ │ (Property Type,   │
│  Location, CV)  │ │  Headcount)    │ │  Education)       │ │  Category, Photo) │
└─────────────────┘ └────────────────┘ └───────────────────┘ └───────────────────┘
                                         │ 1:N
                         ┌───────────────┴───────────────┐
                         │                               │
                 ┌───────┴────────┐              ┌───────┴────────┐
                 │  InternalNote  │              │ NotificationLog│
                 │ (Admin, Note)  │              │ (Type, Status) │
                 └────────────────┘              └────────────────┘
```

- Every submission generates a unique tracking reference: `SKL-YYYYMMDD-XXXXX`
- Database records commit inside a database transaction before notifications are triggered
- Email delivery status or failure logs are recorded in `NotificationLog` without rolling back saved data

---

## 🚀 Quickstart & Local Setup

### 1. Prerequisites
- Python 3.11+
- MySQL 8.x (optional for development, as SQLite test mode is supported)

### 2. Installation
```bash
cd skylink

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` with your MySQL and Email credentials:
```ini
DEBUG=True
SECRET_KEY=your-secure-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# MySQL Database settings
DB_ENGINE=mysql
DB_NAME=skylink_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306

# Email Dispatch
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=Skylink Group <skylinktravels73@gmail.com>
BUSINESS_EMAIL=skylinktravels73@gmail.com
```

### 4. Create Database & Run Migrations
In MySQL:
```sql
CREATE DATABASE IF NOT EXISTS skylink_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
Then run Django migrations:
```bash
python manage.py migrate
```

### 5. Seed Administrative Account & Sample Leads
```bash
python manage.py init_skylink
```
Default staff credentials generated:
- **Username:** `skylink_admin`
- **Password:** `Skylink@2026`

### 6. Collect Static Files & Launch Server
```bash
python manage.py collectstatic --noinput
python manage.py runserver
```
Visit:
- Public Website: http://127.0.0.1:8000/
- Custom Admin Dashboard: http://127.0.0.1:8000/dashboard/
- Django Standard Admin: http://127.0.0.1:8000/admin/

---

## 🧪 Automated Testing

Run the full automated test suite verifying forms, persistence, file uploads, permissions, and spam rejection:
```bash
DB_ENGINE=sqlite python manage.py test submissions
```

### Test Suite Coverage:
- `test_public_pages_load`: Confirms 200 OK on all 13 core and division pages
- `test_general_enquiry_form_valid_and_saved`: Verifies DB persistence and unique reference generation
- `test_honeypot_spam_rejected`: Verifies bots submitting hidden fields are rejected
- `test_employer_enquiry_persists_child_model`: Checks relational `EmployerEnquiry` integrity
- `test_job_application_with_resume_file`: Validates file upload handling and CandidateApplication
- `test_course_admission_persists`: Validates trade academy admissions
- `test_maintenance_service_request`: Tests property classification and service dispatch
- `test_dashboard_unauthorized_redirects_to_login`: Verifies server-side authorization
- `test_dashboard_regular_user_denied`: Restricts non-staff users
- `test_dashboard_staff_user_authorized`: Grants access to operations staff
- `test_admin_update_status_and_add_note`: Tests inline status lifecycle and audit timeline
- `test_csv_export_permissions`: Verifies authorized CSV export response

---

## 🛡️ Production Deployment Checklist

### Gunicorn Execution
```bash
gunicorn skylink.wsgi:application --bind 127.0.0.1:8000 --workers 3 --timeout 120
```

### Nginx Reverse Proxy Configuration Sample
```nginx
server {
    server_name skylinkstaffingsolutions.com www.skylinkstaffingsolutions.com;

    client_max_body_size 15M;

    location /static/ {
        alias /path/to/skylink/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    location /media/ {
        alias /path/to/skylink/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 📄 License & Attribution
© 2026 Skylink Staffing Solutions Pvt. Ltd. All rights reserved.
Registered under the Companies Act, Ministry of Corporate Affairs, Government of India (CIN: U78300BR2025PTC075220).
