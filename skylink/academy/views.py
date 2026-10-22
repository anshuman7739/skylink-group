import logging
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from submissions.models import Submission, CourseAdmission, NotificationLog
from .forms import CourseAdmissionForm

logger = logging.getLogger('skylink')


def home(request):
    return render(request, 'academy/home.html')


def course_admission(request):
    if request.method == 'POST':
        form = CourseAdmissionForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            try:
                with transaction.atomic():
                    sub = Submission.objects.create(
                        division='academy',
                        submission_type='course_admission',
                        full_name=d['name'],
                        phone=d['phone'],
                        email=d.get('email') or 'no-email@skylinkacademy.in',
                        message=d.get('message', ''),
                        source_page='Skill Academy Admission'
                    )
                    CourseAdmission.objects.create(
                        submission=sub,
                        city=d['city'],
                        course=d['course'],
                        preferred_batch=d['preferred_batch'],
                        education_level=d.get('education_level', ''),
                    )

                # Send Admin email notification
                try:
                    course_label = dict(form.fields['course'].choices).get(d['course'], d['course'])
                    batch_label = dict(form.fields['preferred_batch'].choices).get(d['preferred_batch'], d['preferred_batch'])
                    subject = f'[Skylink Academy] New Admission: {d["name"]} — {course_label} ({sub.reference_number})'
                    body = (
                        f"Reference Number: {sub.reference_number}\n"
                        f"Student Name: {d['name']}\n"
                        f"Phone: {d['phone']}\n"
                        f"Email: {d.get('email', 'Not provided')}\n"
                        f"City/District: {d['city']}\n"
                        f"Course: {course_label}\n"
                        f"Batch: {batch_label}\n"
                        f"Education: {d.get('education_level', 'Not specified')}\n\n"
                        f"Notes / Questions:\n{d.get('message', 'N/A')}\n"
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
                    logger.error(f"Email delivery failed for academy admission {sub.reference_number}: {e}")
                    NotificationLog.objects.create(
                        submission=sub,
                        notification_type='admin_alert',
                        recipient=settings.BUSINESS_EMAIL,
                        status='failed',
                        error_details=str(e)
                    )

                # Send confirmation email if email was provided
                if d.get('email'):
                    try:
                        confirm_sub = f"Admission Enquiry Received — Skylink Skill Academy [{sub.reference_number}]"
                        confirm_body = (
                            f"Dear {d['name']},\n\n"
                            f"Thank you for your admission enquiry at Skylink Skill Academy!\n\n"
                            f"Course Selected: {course_label}\n"
                            f"Preferred Batch: {batch_label}\n"
                            f"Your Application Reference Number: {sub.reference_number}\n\n"
                            f"Our Academy Academic Counselor will call or WhatsApp you at {d['phone']} to discuss course fees, batch start dates, and practical lab timings.\n\n"
                            f"Academy Campus: Skylink Tower, Turkha, Nahar Road, Near Bypass Road, Gopalganj, Bihar - 841428\n"
                            f"Helpline: +91 90455 85073 / +91 61564 50214\n"
                        )
                        send_mail(
                            subject=confirm_sub,
                            message=confirm_body,
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

                return redirect('academy:success', ref=sub.reference_number)
            except Exception as e:
                logger.error(f"DB Error saving course admission: {e}")
                messages.error(request, 'Database error while saving admission request. Please call our campus directly.')
    else:
        form = CourseAdmissionForm()

    return render(request, 'academy/course_admission.html', {'form': form})


def success(request, ref):
    return render(request, 'core/success.html', {
        'reference': ref,
        'title': 'Admission Enquiry Registered',
        'message': 'Thank you for your interest in Skylink Skill Academy. Our student admissions counselor will contact you within 24 hours with batch details and fee structures.',
        'division': 'academy',
    })
