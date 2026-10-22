import uuid
import random
import string
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


def generate_reference():
    """Generates a reference number like SKL-YYYYMMDD-XXXXX"""
    date_str = timezone.now().strftime('%Y%m%d')
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f'SKL-{date_str}-{suffix}'


class Submission(models.Model):
    DIVISION_CHOICES = [
        ('staffing', 'Skylink Staffing Solutions'),
        ('academy', 'Skylink Skill Academy'),
        ('maintenance', 'Skylink Maintenance Services'),
        ('general', 'General / Group Corporate'),
    ]

    TYPE_CHOICES = [
        ('general_enquiry', 'General Enquiry'),
        ('employer_enquiry', 'Employer Staffing Enquiry'),
        ('job_application', 'Job Application / Candidate'),
        ('course_admission', 'Skill Academy Admission'),
        ('maintenance_request', 'Maintenance Service Request'),
    ]

    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference_number = models.CharField(
        max_length=25, unique=True, default=generate_reference, editable=False, db_index=True
    )
    division = models.CharField(max_length=20, choices=DIVISION_CHOICES, db_index=True)
    submission_type = models.CharField(max_length=30, choices=TYPE_CHOICES, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', db_index=True)
    source_page = models.CharField(max_length=150, blank=True)

    # Core Contact Information
    full_name = models.CharField(max_length=150)
    email = models.EmailField(db_index=True)
    phone = models.CharField(max_length=25, db_index=True)
    company_name = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField(blank=True, null=True)

    # Internal Workflow
    assigned_to = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_submissions'
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Submission'
        verbose_name_plural = 'Submissions'
        indexes = [
            models.Index(fields=['division', 'status']),
            models.Index(fields=['submission_type', 'status']),
            models.Index(fields=['created_at', 'division']),
        ]

    def __str__(self):
        return f'{self.reference_number} — {self.full_name} ({self.get_submission_type_display()})'

    def get_status_color(self):
        return {
            'new': '#2563EB',        # Blue
            'contacted': '#D97706',  # Amber
            'in_progress': '#7C3AED',# Purple
            'completed': '#16A34A',  # Green
            'rejected': '#DC2626',   # Red
        }.get(self.status, '#4B5563')

    def get_division_badge_color(self):
        return {
            'staffing': '#1B2B6B',    # Navy
            'academy': '#16A34A',     # Green
            'maintenance': '#D97706', # Gold/Amber
            'general': '#4B5563',     # Gray
        }.get(self.division, '#4B5563')


class CandidateApplication(models.Model):
    EXPERIENCE_CHOICES = [
        ('fresher', 'Fresher (0 years)'),
        ('less_1', 'Less than 1 year'),
        ('1_3', '1–3 years'),
        ('3_5', '3–5 years'),
        ('5_10', '5–10 years'),
        ('10_plus', '10+ years'),
    ]

    submission = models.OneToOneField(
        Submission, on_delete=models.CASCADE,
        related_name='candidate_application', primary_key=True
    )
    job_role = models.CharField(max_length=150)
    experience = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES)
    skills = models.TextField()
    preferred_location = models.CharField(max_length=200, blank=True)
    city_state = models.CharField(max_length=200, blank=True)
    resume = models.FileField(upload_to='resumes/%Y/%m/', blank=True, null=True)

    class Meta:
        verbose_name = 'Candidate Application'
        verbose_name_plural = 'Candidate Applications'

    def __str__(self):
        return f'{self.submission.full_name} — {self.job_role}'


class EmployerEnquiry(models.Model):
    submission = models.OneToOneField(
        Submission, on_delete=models.CASCADE,
        related_name='employer_enquiry', primary_key=True
    )
    industry = models.CharField(max_length=150, blank=True)
    required_roles = models.TextField()
    worker_count = models.CharField(max_length=50)
    skills_required = models.TextField(blank=True)
    work_location = models.CharField(max_length=200)
    expected_joining = models.DateField(null=True, blank=True)
    additional_requirements = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Employer Enquiry'
        verbose_name_plural = 'Employer Enquiries'

    def __str__(self):
        return f'{self.submission.company_name or self.submission.full_name} — {self.worker_count}'


class CourseAdmission(models.Model):
    COURSE_CHOICES = [
        ('electrician', 'Electrician Training (3 Months)'),
        ('ac_refrigeration', 'AC & Refrigeration Technician (3 Months)'),
        ('plumbing', 'Plumbing Training (2 Months)'),
        ('safety', 'Safety / HSE Training (1 Month)'),
        ('electrician_adv', 'Advanced Electrician (6 Months)'),
        ('ac_hvac_adv', 'Advanced AC & HVAC (6 Months)'),
    ]

    BATCH_CHOICES = [
        ('morning', 'Morning Batch (8:00 AM – 12:00 PM)'),
        ('afternoon', 'Afternoon Batch (12:00 PM – 4:00 PM)'),
        ('evening', 'Evening Batch (4:00 PM – 8:00 PM)'),
        ('weekend', 'Weekend Intensive (Sat & Sun)'),
    ]

    EDU_CHOICES = [
        ('below_10', 'Below Class 10'),
        ('class_10', 'Class 10 (Matriculation)'),
        ('class_12', 'Class 12 (Intermediate)'),
        ('diploma', 'Diploma / ITI'),
        ('graduate', 'Graduate'),
        ('other', 'Other'),
    ]

    submission = models.OneToOneField(
        Submission, on_delete=models.CASCADE,
        related_name='course_admission', primary_key=True
    )
    city = models.CharField(max_length=150, blank=True)
    course = models.CharField(max_length=40, choices=COURSE_CHOICES)
    preferred_batch = models.CharField(max_length=20, choices=BATCH_CHOICES)
    education_level = models.CharField(max_length=20, choices=EDU_CHOICES, blank=True)

    class Meta:
        verbose_name = 'Course Admission'
        verbose_name_plural = 'Course Admissions'

    def __str__(self):
        return f'{self.submission.full_name} — {self.get_course_display()}'


class MaintenanceRequest(models.Model):
    PROPERTY_CHOICES = [
        ('residential_apartment', 'Residential — Apartment / Flat'),
        ('residential_house', 'Residential — Independent House / Villa'),
        ('commercial_office', 'Commercial — Office / Corporate Space'),
        ('commercial_shop', 'Commercial — Shop / Showroom / Mall'),
        ('commercial_warehouse', 'Commercial — Warehouse / Industrial Unit'),
        ('institutional', 'Institutional — School / College / Hospital / Govt'),
        ('other', 'Other Property Type'),
    ]

    SERVICE_CHOICES = [
        ('electrical', 'Electrical Services & Wiring'),
        ('ac_hvac', 'AC & HVAC Maintenance / Installation'),
        ('plumbing', 'Plumbing & Pipe Fitting'),
        ('handyman', 'Handyman & General Repairs'),
        ('facility_management', 'Full Facility Management (AMC)'),
        ('multiple', 'Multiple / Turnkey Maintenance'),
    ]

    submission = models.OneToOneField(
        Submission, on_delete=models.CASCADE,
        related_name='maintenance_request', primary_key=True
    )
    property_type = models.CharField(max_length=40, choices=PROPERTY_CHOICES)
    service_category = models.CharField(max_length=30, choices=SERVICE_CHOICES)
    property_location = models.CharField(max_length=300)
    preferred_date = models.DateField(null=True, blank=True)
    attachment = models.FileField(upload_to='maintenance_attachments/%Y/%m/', blank=True, null=True)

    class Meta:
        verbose_name = 'Maintenance Request'
        verbose_name_plural = 'Maintenance Requests'

    def __str__(self):
        return f'{self.submission.full_name} — {self.get_service_category_display()}'


class NotificationLog(models.Model):
    TYPE_CHOICES = [
        ('admin_alert', 'Admin Alert Email'),
        ('confirmation', 'Visitor Confirmation Email'),
    ]
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]

    submission = models.ForeignKey(
        Submission, on_delete=models.CASCADE, related_name='notifications'
    )
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    recipient = models.EmailField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    provider_message_id = models.CharField(max_length=200, blank=True)
    error_details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification Log'
        verbose_name_plural = 'Notification Logs'

    def __str__(self):
        return f'{self.submission.reference_number} — {self.notification_type} [{self.status}]'


class InternalNote(models.Model):
    submission = models.ForeignKey(
        Submission, on_delete=models.CASCADE, related_name='internal_notes'
    )
    administrator = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='notes'
    )
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Internal Note'
        verbose_name_plural = 'Internal Notes'

    def __str__(self):
        return f'Note on {self.submission.reference_number}'
