from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from submissions.models import (
    Submission, CandidateApplication, EmployerEnquiry,
    CourseAdmission, MaintenanceRequest, InternalNote, NotificationLog
)


class Command(BaseCommand):
    help = 'Initializes Skylink default staff administrator and sample pipeline records'

    def handle(self, *args, **options):
        # 1. Admin Superuser
        admin_user, created = User.objects.get_or_create(
            username='skylink_admin',
            defaults={
                'email': 'skylinktravels73@gmail.com',
                'first_name': 'Mahtab',
                'last_name': 'Alam',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('Skylink@2026')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created default staff superuser: skylink_admin / Skylink@2026'))
        else:
            self.stdout.write(self.style.WARNING('Superuser skylink_admin already exists.'))

        # 2. Sample Staffing Employer Enquiry
        if not Submission.objects.filter(company_name='Al-Futtaim Engineering').exists():
            sub1 = Submission.objects.create(
                division='staffing',
                submission_type='employer_enquiry',
                status='contacted',
                full_name='Tariq Al-Mansoor',
                phone='+971 50 123 4567',
                email='tariq.mansoor@alfuttaim-sample.ae',
                company_name='Al-Futtaim Engineering',
                message='Urgent requirement for Gulf certified HVAC technicians.',
                assigned_to=admin_user,
                source_page='Employer Requisition'
            )
            EmployerEnquiry.objects.create(
                submission=sub1,
                industry='HVAC & MEP Contracting',
                required_roles='25 AC Technicians, 10 Duct Fabricators',
                worker_count='16-50 workers',
                skills_required='Valid trade certificate, minimum 3 years Gulf experience',
                work_location='Dubai, UAE',
                additional_requirements='Accommodation and medical insurance provided by employer.'
            )
            InternalNote.objects.create(
                submission=sub1,
                administrator=admin_user,
                note='Interview date scheduled for next Tuesday at Gopalganj testing bay.'
            )
            NotificationLog.objects.create(
                submission=sub1,
                notification_type='admin_alert',
                recipient='skylinktravels73@gmail.com',
                status='sent'
            )

        # 3. Sample Candidate Application
        if not Submission.objects.filter(email='shahid.ansari@sample.com').exists():
            sub2 = Submission.objects.create(
                division='staffing',
                submission_type='job_application',
                status='in_progress',
                full_name='Shahid Ansari',
                phone='+91 98350 11223',
                email='shahid.ansari@sample.com',
                message='Job Role: Electrician | Experience: 5_10',
                assigned_to=admin_user,
                source_page='Careers'
            )
            CandidateApplication.objects.create(
                submission=sub2,
                job_role='Electrician',
                experience='5_10',
                skills='Industrial wiring, control panels, motor rewinding',
                city_state='Gopalganj, Bihar',
                preferred_location='Saudi Arabia'
            )

        # 4. Sample Skill Academy Admission
        if not Submission.objects.filter(email='vikram.singh@sample.com').exists():
            sub3 = Submission.objects.create(
                division='academy',
                submission_type='course_admission',
                status='new',
                full_name='Vikram Kumar Singh',
                phone='+91 91234 56780',
                email='vikram.singh@sample.com',
                message='Interested in AC repair trade',
                source_page='Skill Academy'
            )
            CourseAdmission.objects.create(
                submission=sub3,
                city='Thawe, Gopalganj',
                course='ac_refrigeration',
                preferred_batch='morning',
                education_level='class_12'
            )

        # 5. Sample Maintenance Request
        if not Submission.objects.filter(email='gopalganj.hotel@sample.com').exists():
            sub4 = Submission.objects.create(
                division='maintenance',
                submission_type='maintenance_request',
                status='new',
                full_name='Rajesh Gupta',
                phone='+91 94312 99887',
                email='gopalganj.hotel@sample.com',
                company_name='Hotel Highway Regency',
                message='Centralized AC chiller pump making abnormal vibration noise.',
                source_page='Maintenance Booking'
            )
            MaintenanceRequest.objects.create(
                submission=sub4,
                property_type='commercial_office',
                service_category='ac_hvac',
                property_location='Bypass Road, Gopalganj, Bihar',
            )

        self.stdout.write(self.style.SUCCESS('Successfully initialized Skylink administrative user and sample records.'))
