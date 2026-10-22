import logging
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from submissions.models import Submission, MaintenanceRequest, NotificationLog
from .forms import MaintenanceRequestForm

logger = logging.getLogger('skylink')


def home(request):
    return render(request, 'maintenance/home.html')


def service_request(request):
    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST, request.FILES)
        if form.is_valid():
            d = form.cleaned_data
            try:
                with transaction.atomic():
                    sub = Submission.objects.create(
                        division='maintenance',
                        submission_type='maintenance_request',
                        full_name=d['name'],
                        phone=d['phone'],
                        email=d['email'],
                        message=d['problem_description'],
                        source_page='Request a Service'
                    )
                    maint = MaintenanceRequest(
                        submission=sub,
                        property_type=d['property_type'],
                        service_category=d['service_category'],
                        property_location=d['location'],
                        preferred_date=d.get('preferred_date'),
                    )
                    if d.get('attachment'):
                        maint.attachment = d['attachment']
                    maint.save()

                # Send Admin notification
                try:
                    category_label = dict(form.fields['service_category'].choices).get(d['service_category'], d['service_category'])
                    prop_label = dict(form.fields['property_type'].choices).get(d['property_type'], d['property_type'])
                    subject = f'[Skylink Maintenance] Service Request: {category_label} ({sub.reference_number})'
                    body = (
                        f"Reference Number: {sub.reference_number}\n"
                        f"Customer Name: {d['name']}\n"
                        f"Phone: {d['phone']}\n"
                        f"Email: {d['email']}\n"
                        f"Property Type: {prop_label}\n"
                        f"Service: {category_label}\n"
                        f"Property Location: {d['location']}\n"
                        f"Preferred Date: {d.get('preferred_date', 'Urgent / ASAP')}\n\n"
                        f"Problem Description:\n{d['problem_description']}\n\n"
                        f"Photo/Doc Attached: {'Yes (see Admin Portal)' if maint.attachment else 'No'}\n"
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
                    logger.error(f"Email failure for maintenance request {sub.reference_number}: {e}")
                    NotificationLog.objects.create(
                        submission=sub,
                        notification_type='admin_alert',
                        recipient=settings.BUSINESS_EMAIL,
                        status='failed',
                        error_details=str(e)
                    )

                # Send confirmation email to customer
                try:
                    confirm_sub = f"Service Request Confirmed — Skylink Maintenance Services [{sub.reference_number}]"
                    confirm_body = (
                        f"Dear {d['name']},\n\n"
                        f"We have received your service request for {category_label}.\n"
                        f"Your Work Order Reference: {sub.reference_number}\n\n"
                        f"Our maintenance supervisor will contact you on {d['phone']} to confirm technician dispatch time and inspection details.\n\n"
                        f"Service Hotline: +91 90455 85073 / +91 61564 50214\n"
                        f"Skylink Maintenance Services\n"
                        f"Gopalganj, Bihar\n"
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

                return redirect('maintenance:success', ref=sub.reference_number)
            except Exception as e:
                logger.error(f"DB Error saving maintenance request: {e}")
                messages.error(request, 'Database error while registering service request. Please call our 24/7 helpline.')
    else:
        form = MaintenanceRequestForm()

    return render(request, 'maintenance/service_request.html', {'form': form})


def success(request, ref):
    return render(request, 'core/success.html', {
        'reference': ref,
        'title': 'Service Request Booked Successfully',
        'message': 'Thank you for choosing Skylink Maintenance Services. Our operations coordinator will call you shortly to confirm technician arrival.',
        'division': 'maintenance',
    })
