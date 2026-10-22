# Skylink Group — Developer & Customization Guide

This guide explains how your codebase is structured and how to easily make changes.

---

## 📁 1. Project Folder Locations

- **Active Project Directory:** `/Users/shubhamkumar/Desktop/skill_india/skylink`
- **Standalone Backup Copy:** `/Users/shubhamkumar/Desktop/skylink_backup_copy`
- **Compressed Zip Archive:** `/Users/shubhamkumar/Desktop/skill_india/skylink_full_backup.zip`
- **Git Version Control:** Initialized in `/Users/shubhamkumar/Desktop/skill_india` (run `git status` or `git log` anytime).

---

## 🎨 2. How to Change Website Content & Templates

All HTML templates are located in: `skylink/templates/`

| If you want to change... | File to edit |
| :--- | :--- |
| **Header, Navigation bar & Menu links** | `templates/navbar.html` |
| **Footer, Contact details & Social links** | `templates/footer.html` |
| **Homepage (Hero, 3 Divisions, Why Choose Us)** | `templates/core/home.html` |
| **About Us page (History, Leadership, Values)** | `templates/core/about.html` |
| **All Services overview page** | `templates/core/all_services.html` |
| **General Contact page & form layout** | `templates/core/contact.html` |
| **Staffing Solutions division homepage** | `templates/staffing/home.html` |
| **Employer Staffing Enquiry form** | `templates/staffing/employer_enquiry.html` |
| **Job Application / Careers form** | `templates/staffing/job_application.html` |
| **Skill Academy division homepage** | `templates/academy/home.html` |
| **Course Admission form** | `templates/academy/course_admission.html` |
| **Maintenance Services division homepage** | `templates/maintenance/home.html` |
| **Request a Service form** | `templates/maintenance/service_request.html` |
| **Privacy Policy** | `templates/core/privacy_policy.html` |
| **Terms and Conditions** | `templates/core/terms.html` |
| **Custom Admin Dashboard UI** | `templates/admin_custom/dashboard.html` |
| **Admin Submission Detail & Notes UI** | `templates/admin_custom/submission_detail.html` |

---

## 🎨 3. How to Change Colours and Styling

- **Tailwind CSS & Custom Utility Classes:** `skylink/static/css/skylink.css`
- **Branding Palette:**
  - Corporate Navy: `#0B1B3D`
  - Gold Accent: `#D4AF37`
  - Academy Green: `#16A34A`
  - Maintenance Gold/Amber: `#D97706`
  - Background Neutral: `#F8FAFC`

---

## 🖼️ 4. How to Change Logos and Images

Branding and logo files are saved in:
- `skylink/static/images/logo.svg` (SVG Vector Corporate Logo)
- `skylink/static/images/branding/` (Reference flyers, ID card, banner photos)

Whenever you add or replace images, run:
```bash
python manage.py collectstatic --noinput
```

---

## ⚙️ 5. How to Change Contact Details Globally

The company phone numbers, email, and address are centrally defined in:
`skylink/core/context_processors.py`

```python
'business_phone1': '+91 90455 85073',
'business_phone2': '+91 61564 50214',
'business_email': 'skylinktravels73@gmail.com',
'business_address': 'Turkaha, Thawe Road, Near Masjid, Gopalganj, Bihar - 841428',
'head_office': 'Skylink Tower Turkha, Nahar Road, Near Bypass Road, Gopalganj, Bihar - 841428',
'cin': 'U78300BR2025PTC075220',
'md_name': 'Er. Mahtab Alam (Guddu)',
```
Editing this file updates all headers, footers, and contact cards across the entire website automatically!

---

## 🗄️ 6. How to Switch from SQLite to MySQL

Open `skylink/.env`:
```ini
DB_ENGINE=mysql
DB_NAME=skylink_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306
```
Then run:
```bash
python manage.py migrate
python manage.py init_skylink
```

---

## 🚀 7. Starting the Server Locally

```bash
cd /Users/shubhamkumar/Desktop/skill_india/skylink
/opt/anaconda3/bin/python3 manage.py runserver 127.0.0.1:8000
```

Admin credentials:
- URL: `http://127.0.0.1:8000/dashboard/login/`
- Username: `skylink_admin`
- Password: `Skylink@2026`
