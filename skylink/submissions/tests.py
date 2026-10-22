import io
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail
from submissions.models import (
    Submission, CandidateApplication, EmployerEnquiry,
    CourseAdmission, MaintenanceRequest, NotificationLog, InternalNote
)
from core.forms import GeneralEnquiryForm
from staffing.forms import JobApplicationForm, EmployerEnquiryForm
from academy.forms import CourseAdmissionForm
from maintenance.forms import MaintenanceRequestForm


class SkylinkFormsAndPersistenceTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='admin_staff',
            password='Password@123',
            is_staff=True,
            first_name='Admin',
            last_name='User'
        )
        self.regular_user = User.objects.create_user(
            username='regular_user',
            password='Password@123',
            is_staff=False
        )

    # 1. Public Pages Response Checks
    def test_public_pages_load(self):
        urls = [
            reverse('core:home'),
            reverse('core:about'),
            reverse('core:services'),
            reverse('core:contact'),
            reverse('core:privacy_policy'),
            reverse('core:terms'),
            reverse('staffing:home'),
            reverse('staffing:employer_enquiry'),
            reverse('staffing:job_application'),
            reverse('academy:home'),
            reverse('academy:course_admission'),
            reverse('maintenance:home'),
            reverse('maintenance:service_request'),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"Failed loading {url}")
            self.assertContains(response, 'Skylink')

    # 2. General Enquiry Submission & Persistence
    def test_general_enquiry_form_valid_and_saved(self):
        payload = {
            'name': 'Ramesh Kumar',
            'phone': '9876543210',
            'email': 'ramesh@example.com',
            'company_name': 'Ramesh Enterprises',
            'division': 'staffing',
            'enquiry_type': 'service_enquiry',
            'message': 'We require 20 certified electricians for our site in Gujarat.',
            'consent': 'on',
            'website': '',  # Honeypot empty
        }
        response = self.client.post(reverse('core:contact'), data=payload)
        self.assertEqual(response.status_code, 302)  # Redirects to success
        
        # Verify persistence
        sub = Submission.objects.filter(email='ramesh@example.com').first()
        self.assertIsNotNone(sub)
        self.assertEqual(sub.full_name, 'Ramesh Kumar')
        self.assertEqual(sub.division, 'staffing')
        self.assertTrue(sub.reference_number.startswith('SKL-'))
        self.assertEqual(sub.status, 'new')

    # 3. Honeypot Spam Prevention
    def test_honeypot_spam_rejected(self):
        payload = {
            'name': 'Bot Spammer',
            'phone': '9876543210',
            'email': 'bot@spam.com',
            'division': 'general',
            'enquiry_type': 'information',
            'message': 'Buy cheap backlinks',
            'consent': 'on',
            'website': 'http://spambot.com',  # Honeypot filled!
        }
        response = self.client.post(reverse('core:contact'), data=payload)
        self.assertEqual(response.status_code, 200)  # Form re-rendered with error
        self.assertFalse(Submission.objects.filter(email='bot@spam.com').exists())

    # 4. Employer Enquiry Full Persistence
    def test_employer_enquiry_persists_child_model(self):
        payload = {
            'contact_person': 'Anita Sharma',
            'company_name': 'Gulf Contracting Co.',
            'phone': '9123456789',
            'email': 'anita@gulfcontracting.com',
            'industry': 'Oil & Gas',
            'job_roles_required': '15 Welder 6G, 10 Pipe Fitters',
            'worker_count': '16-50 workers',
            'skills_required': 'TIG/ARC certified with valid passport',
            'work_location': 'Dammam, Saudi Arabia',
            'expected_joining': '2026-11-01',
            'requirements': 'Food, accommodation and flights provided',
            'website': '',
        }
        response = self.client.post(reverse('staffing:employer_enquiry'), data=payload)
        self.assertEqual(response.status_code, 302)

        sub = Submission.objects.get(email='anita@gulfcontracting.com')
        self.assertEqual(sub.submission_type, 'employer_enquiry')
        self.assertEqual(sub.company_name, 'Gulf Contracting Co.')
        
        # Check child model
        employer_detail = sub.employer_enquiry
        self.assertEqual(employer_detail.worker_count, '16-50 workers')
        self.assertEqual(employer_detail.work_location, 'Dammam, Saudi Arabia')

    # 5. Candidate Application with Resume Upload
    def test_job_application_with_resume_file(self):
        fake_resume = SimpleUploadedFile(
            'cv_mohammad.pdf',
            b'%PDF-1.4 Fake PDF Content for Resume',
            content_type='application/pdf'
        )
        payload = {
            'full_name': 'Mohammad Tariq',
            'phone': '9045585000',
            'email': 'tariq@example.com',
            'city_state': 'Gopalganj, Bihar',
            'job_role': 'AC / HVAC Technician',
            'experience': '3_5',
            'preferred_location': 'Dubai, UAE',
            'skills': 'VRV, Split AC repair, copper brazing, gas charging R32',
            'resume': fake_resume,
            'privacy_consent': 'on',
            'website': '',
        }
        response = self.client.post(reverse('staffing:job_application'), data=payload)
        self.assertEqual(response.status_code, 302)

        sub = Submission.objects.get(email='tariq@example.com')
        candidate = sub.candidate_application
        self.assertEqual(candidate.job_role, 'AC / HVAC Technician')
        self.assertTrue(candidate.resume.name.endswith('.pdf'))

    # 6. Academy Course Admission
    def test_course_admission_persists(self):
        payload = {
            'name': 'Sunil Verma',
            'phone': '9812345678',
            'email': 'sunil@gmail.com',
            'city': 'Siwan, Bihar',
            'course': 'electrician',
            'preferred_batch': 'morning',
            'education_level': 'class_12',
            'message': 'Hostel accommodation required',
            'website': '',
        }
        response = self.client.post(reverse('academy:course_admission'), data=payload)
        self.assertEqual(response.status_code, 302)

        sub = Submission.objects.get(email='sunil@gmail.com')
        self.assertEqual(sub.division, 'academy')
        self.assertEqual(sub.course_admission.course, 'electrician')

    # 7. Maintenance Request Booking
    def test_maintenance_service_request(self):
        payload = {
            'name': 'Dr. Alok Verma',
            'phone': '9431200000',
            'email': 'alok@clinic.in',
            'property_type': 'commercial_office',
            'service_category': 'ac_hvac',
            'location': 'Near Gandhi Chowk, Gopalganj',
            'problem_description': '2-Ton Split AC compressor tripping after 10 minutes of cooling',
            'preferred_date': '2026-10-25',
            'website': '',
        }
        response = self.client.post(reverse('maintenance:service_request'), data=payload)
        self.assertEqual(response.status_code, 302)

        sub = Submission.objects.get(email='alok@clinic.in')
        self.assertEqual(sub.division, 'maintenance')
        self.assertEqual(sub.maintenance_request.service_category, 'ac_hvac')

    # 8. Admin Security & Authorization
    def test_dashboard_unauthorized_redirects_to_login(self):
        # Anonymous user cannot access dashboard
        response = self.client.get(reverse('submissions:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard/login/', response.url)

    def test_dashboard_regular_user_denied(self):
        # Non-staff user logged in
        self.client.login(username='regular_user', password='Password@123')
        response = self.client.get(reverse('submissions:dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_staff_user_authorized(self):
        self.client.login(username='admin_staff', password='Password@123')
        response = self.client.get(reverse('submissions:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Corporate Submissions Dashboard')

    # 9. Status Update & Internal Note
    def test_admin_update_status_and_add_note(self):
        sub = Submission.objects.create(
            division='staffing',
            submission_type='general_enquiry',
            full_name='Test Client',
            phone='9999999999',
            email='test@client.com'
        )
        self.client.login(username='admin_staff', password='Password@123')
        
        # Update status
        self.client.post(reverse('submissions:detail', kwargs={'pk': sub.id}), {
            'action': 'update_status',
            'status': 'contacted'
        })
        sub.refresh_from_db()
        self.assertEqual(sub.status, 'contacted')

        # Add internal note
        self.client.post(reverse('submissions:detail', kwargs={'pk': sub.id}), {
            'action': 'add_note',
            'note': 'Spoke with client on phone. Agreed on quotation.'
        })
        self.assertEqual(sub.internal_notes.count(), 2)  # 1 from status change + 1 manual

    # 10. CSV Export Permission
    def test_csv_export_permissions(self):
        # Anonymous denied
        response = self.client.get(reverse('submissions:export'))
        self.assertEqual(response.status_code, 302)

        # Staff allowed
        self.client.login(username='admin_staff', password='Password@123')
        response = self.client.get(reverse('submissions:export'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('attachment; filename=', response['Content-Disposition'])
