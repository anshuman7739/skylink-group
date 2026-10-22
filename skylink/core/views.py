import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from submissions.models import Submission, NotificationLog
from .forms import GeneralEnquiryForm

logger = logging.getLogger('skylink')


def home(request):
    return render(request, 'core/home.html')


def about(request):
    return render(request, 'core/about.html')


def all_services(request):
    return render(request, 'core/all_services.html')


def contact(request):
    if request.method == 'POST':
        form = GeneralEnquiryForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                with transaction.atomic():
                    sub = Submission.objects.create(
                        division=data['division'],
                        submission_type='general_enquiry',
                        full_name=data['name'],
                        phone=data['phone'],
                        email=data['email'],
                        company_name=data.get('company_name', ''),
                        message=data['message'],
                        source_page='Contact Us'
                    )

                # Send email notification after successful DB commit
                try:
                    subject = f'[Skylink Group] General Enquiry — {sub.reference_number}'
                    body = (
                        f"Reference Number: {sub.reference_number}\n"
                        f"Division: {sub.get_division_display()}\n"
                        f"Full Name: {sub.full_name}\n"
                        f"Phone: {sub.phone}\n"
                        f"Email: {sub.email}\n"
                        f"Company: {sub.company_name or 'N/A'}\n"
                        f"Enquiry Type: {data.get('enquiry_type', 'General')}\n\n"
                        f"Message:\n{sub.message}\n"
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
                    logger.error(f"Email delivery failed for {sub.reference_number}: {e}")
                    NotificationLog.objects.create(
                        submission=sub,
                        notification_type='admin_alert',
                        recipient=settings.BUSINESS_EMAIL,
                        status='failed',
                        error_details=str(e)
                    )

                return redirect('core:contact_success', ref=sub.reference_number)
            except Exception as e:
                logger.error(f"Failed saving enquiry: {e}")
                messages.error(request, 'A database error occurred while submitting. Please try again or call us directly.')
    else:
        form = GeneralEnquiryForm()

    return render(request, 'core/contact.html', {'form': form})


def contact_success(request, ref):
    return render(request, 'core/success.html', {
        'reference': ref,
        'title': 'Enquiry Submitted Successfully',
        'message': 'Thank you for reaching out to Skylink Group of Companies. Our representative will contact you shortly.',
    })


def privacy_policy(request):
    return render(request, 'core/privacy_policy.html')


def terms(request):
    return render(request, 'core/terms.html')


def handler404(request, exception):
    return render(request, 'core/404.html', status=404)


def handler500(request):
    return render(request, 'core/500.html', status=500)
