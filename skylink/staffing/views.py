import logging
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from submissions.models import Submission, CandidateApplication, EmployerEnquiry, NotificationLog
from .forms import JobApplicationForm, EmployerEnquiryForm

logger = logging.getLogger('skylink')


def home(request):
    return render(request, 'staffing/home.html')


def employer_enquiry(request):
    if request.method == 'POST':
        form = EmployerEnquiryForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            try:
                with transaction.atomic():
                    sub = Submission.objects.create(
                        division='staffing',
                        submission_type='employer_enquiry',
                        full_name=d['contact_person'],
                        company_name=d['company_name'],
                        phone=d['phone'],
                        email=d['email'],
                        message=d.get('requirements', ''),
                        source_page='Employer Staffing Enquiry'
                    )
                    EmployerEnquiry.objects.create(
                        submission=sub,
                        industry=d.get('industry', ''),
                        required_roles=d['job_roles_required'],
                        worker_count=d['worker_count'],
                        skills_required=d.get('skills_required', ''),
                        work_location=d['work_location'],
                        expected_joining=d.get('expected_joining'),
                        additional_requirements=d.get('requirements', ''),
                    )

                # Send email notification to business
                try:
                    subject = f'[Skylink Staffing] Employer Enquiry — {d["company_name"]} ({sub.reference_number})'
                    body = (
                        f"Reference Number: {sub.reference_number}\n"
                        f"Company Name: {d['company_name']}\n"
                        f"Contact Person: {d['contact_person']}\n"
                        f"Phone: {d['phone']}\n"
                        f"Email: {d['email']}\n"
                        f"Industry: {d.get('industry', 'N/A')}\n"
                        f"Work Location: {d['work_location']}\n"
                        f"Worker Count: {d['worker_count']}\n"
                        f"Expected Joining: {d.get('expected_joining', 'Immediate')}\n\n"
                        f"Required Job Roles:\n{d['job_roles_required']}\n\n"
                        f"Skills / Certifications Required:\n{d.get('skills_required', 'N/A')}\n\n"
                        f"Additional Requirements:\n{d.get('requirements', 'N/A')}\n"
                    )
                    send_mail(
                        subject=subject,
                        message=body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[settings.BUSINESS_EMAIL],
                        fail_silently=False,
                    )
                    NotificationLog.objects.create(
                        submission=sub,
                        notification_type='admin_alert',
                        recipient=settings.BUSINESS_EMAIL,
                        status='sent'
                    )
                except Exception as e:
                    logger.error(f"Email failure for employer enquiry {sub.reference_number}: {e}")
                    NotificationLog.objects.create(
                        submission=sub,
                        notification_type='admin_alert',
                        recipient=settings.BUSINESS_EMAIL,
                        status='failed',
                        error_details=str(e)
                    )

                return redirect('staffing:success', ref=sub.reference_number)
            except Exception as e:
                logger.error(f"DB Error saving employer enquiry: {e}")
                messages.error(request, 'Database error while saving enquiry. Please contact us directly.')
    else:
        form = EmployerEnquiryForm()

    return render(request, 'staffing/employer_enquiry.html', {'form': form})


def job_application(request):
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            d = form.cleaned_data
            try:
                with transaction.atomic():
                    sub = Submission.objects.create(
                        division='staffing',
                        submission_type='job_application',
                        full_name=d['full_name'],
                        phone=d['phone'],
                        email=d['email'],
                        message=f"Job Role: {d['job_role']} | Experience: {d['experience']}",
                        source_page='Careers & Job Application'
                    )
                    candidate = CandidateApplication(
                        submission=sub,
                        job_role=d['job_role'],
                        experience=d['experience'],
                        skills=d['skills'],
                        preferred_location=d.get('preferred_location', ''),
                        city_state=d['city_state'],
                    )
                    if d.get('resume'):
                        candidate.resume = d['resume']
                    candidate.save()

                # Send Admin notification
                try:
                    subject = f'[Skylink Careers] Job Application: {d["full_name"]} - {d["job_role"]} ({sub.reference_number})'
                    body = (
                        f"Reference Number: {sub.reference_number}\n"
                        f"Candidate Name: {d['full_name']}\n"
                        f"Phone: {d['phone']}\n"
                        f"Email: {d['email']}\n"
                        f"Location: {d['city_state']}\n"
                        f"Job Role: {d['job_role']}\n"
                        f"Experience: {d['experience']}\n"
                        f"Preferred Location: {d.get('preferred_location', 'Any')}\n\n"
                        f"Skills & Highlights:\n{d['skills']}\n\n"
                        f"Resume Attached: {'Yes (see Admin Portal)' if candidate.resume else 'No'}\n"
                    )
                    send_mail(
                        subject=subject,
                        message=body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[settings.BUSINESS_EMAIL],
                        fail_silently=False,
                    )
                    NotificationLog.objects.create(
                        submission=sub,
                        notification_type='admin_alert',
                        recipient=settings.BUSINESS_EMAIL,
                        status='sent'
                    )
                except Exception as e:
                    logger.error(f"Email failure for candidate application {sub.reference_number}: {e}")
                    NotificationLog.objects.create(
                        submission=sub,
                        notification_type='admin_alert',
                        recipient=settings.BUSINESS_EMAIL,
                        status='failed',
                        error_details=str(e)
                    )

                # Send Confirmation Email to Candidate
                try:
                    candidate_subject = f'Application Received — Skylink Staffing Solutions [{sub.reference_number}]'
                    candidate_body = (
                        f"Dear {d['full_name']},\n\n"
                        f"Thank you for applying for the position of {d['job_role']} with Skylink Staffing Solutions Pvt. Ltd.\n\n"
                        f"Your application has been registered with Reference Number: {sub.reference_number}.\n"
                        f"Our recruitment team will review your profile against active client mandates (Domestic & Overseas).\n"
                        f"If shortlisted, you will receive a call or WhatsApp on {d['phone']}.\n\n"
                        f"Best Regards,\n"
                        f"Recruitment Team\n"
                        f"Skylink Staffing Solutions Pvt. Ltd.\n"
                        f"Gopalganj, Bihar | Phone: +91 90455 85073\n"
                    )
                    send_mail(
                        subject=candidate_subject,
                        message=candidate_body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[d['email']],
                        fail_silently=True,
                    )
                    NotificationLog.objects.create(
                        submission=sub,
                        notification_type='confirmation',
                        recipient=d['email'],
                        status='sent'
                    )
                except Exception:
                    pass

                return redirect('staffing:success', ref=sub.reference_number)
            except Exception as e:
                logger.error(f"DB Error saving job application: {e}")
                messages.error(request, 'Database error while saving application. Please try again.')
    else:
        form = JobApplicationForm()

    return render(request, 'staffing/job_application.html', {'form': form})


def success(request, ref):
    return render(request, 'core/success.html', {
        'reference': ref,
        'title': 'Submission Received Successfully',
        'message': 'Thank you for reaching out to Skylink Staffing Solutions. Our recruitment and HR consulting team will review your details and contact you shortly.',
        'division': 'staffing',
    })
