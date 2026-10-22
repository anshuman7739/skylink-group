import csv
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from .models import (
    Submission, CandidateApplication, EmployerEnquiry,
    CourseAdmission, MaintenanceRequest, NotificationLog, InternalNote
)


def is_staff_check(user):
    return user.is_authenticated and user.is_staff


def admin_login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('submissions:dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                next_url = request.GET.get('next') or 'submissions:dashboard'
                return redirect(next_url)
            else:
                messages.error(request, 'Access denied. Administrator privileges required.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'admin_custom/login.html', {'form': form})


def admin_logout_view(request):
    logout(request)
    messages.info(request, 'You have been securely logged out.')
    return redirect('submissions:admin_login')


@login_required(login_url='submissions:admin_login')
@user_passes_test(is_staff_check, login_url='submissions:admin_login')
def dashboard(request):
    qs = Submission.objects.all().select_related('assigned_to')

    # Comprehensive KPIs
    stats = {
        'total': qs.count(),
        'new': qs.filter(status='new').count(),
        'contacted': qs.filter(status='contacted').count(),
        'in_progress': qs.filter(status='in_progress').count(),
        'completed': qs.filter(status='completed').count(),
        'rejected': qs.filter(status='rejected').count(),
    }

    # Division distribution
    division_counts = {
        'staffing': qs.filter(division='staffing').count(),
        'academy': qs.filter(division='academy').count(),
        'maintenance': qs.filter(division='maintenance').count(),
        'general': qs.filter(division='general').count(),
    }

    # Filter & Search
    query = request.GET.get('q', '').strip()
    division = request.GET.get('division', '')
    submission_type = request.GET.get('type', '')
    status = request.GET.get('status', '')
    date_str = request.GET.get('date', '')

    filtered_qs = qs
    if query:
        filtered_qs = filtered_qs.filter(
            Q(reference_number__icontains=query) |
            Q(full_name__icontains=query) |
            Q(phone__icontains=query) |
            Q(email__icontains=query) |
            Q(company_name__icontains=query)
        )
    if division:
        filtered_qs = filtered_qs.filter(division=division)
    if submission_type:
        filtered_qs = filtered_qs.filter(submission_type=submission_type)
    if status:
        filtered_qs = filtered_qs.filter(status=status)
    if date_str:
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d').date()
            filtered_qs = filtered_qs.filter(created_at__date=dt)
        except ValueError:
            pass

    # Pagination: 20 per page
    paginator = Paginator(filtered_qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Recent enquiries (top 5 for quick overview card)
    recent_submissions = qs[:5]

    context = {
        'stats': stats,
        'division_counts': division_counts,
        'page_obj': page_obj,
        'query': query,
        'division_filter': division,
        'type_filter': submission_type,
        'status_filter': status,
        'date_filter': date_str,
        'division_choices': Submission.DIVISION_CHOICES,
        'type_choices': Submission.TYPE_CHOICES,
        'status_choices': Submission.STATUS_CHOICES,
        'recent_submissions': recent_submissions,
    }
    return render(request, 'admin_custom/dashboard.html', context)


@login_required(login_url='submissions:admin_login')
@user_passes_test(is_staff_check, login_url='submissions:admin_login')
def submission_detail(request, pk):
    sub = get_object_or_404(Submission, pk=pk)

    # Fetch corresponding division specific detail
    candidate_app = getattr(sub, 'candidate_application', None)
    employer_enq = getattr(sub, 'employer_enquiry', None)
    course_adm = getattr(sub, 'course_admission', None)
    maint_req = getattr(sub, 'maintenance_request', None)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_status':
            new_status = request.POST.get('status')
            if new_status in dict(Submission.STATUS_CHOICES):
                old_status_display = sub.get_status_display()
                sub.status = new_status
                sub.save(update_fields=['status', 'updated_at'])
                InternalNote.objects.create(
                    submission=sub,
                    administrator=request.user,
                    note=f'Status changed from {old_status_display} to {sub.get_status_display()}'
                )
                messages.success(request, f'Status updated to "{sub.get_status_display()}".')

        elif action == 'add_note':
            note_text = request.POST.get('note', '').strip()
            if note_text:
                InternalNote.objects.create(
                    submission=sub,
                    administrator=request.user,
                    note=note_text
                )
                messages.success(request, 'Internal note recorded successfully.')

        elif action == 'assign_user':
            user_id = request.POST.get('assigned_to')
            if user_id:
                try:
                    staff_user = User.objects.get(pk=user_id, is_staff=True)
                    sub.assigned_to = staff_user
                    sub.save(update_fields=['assigned_to', 'updated_at'])
                    messages.success(request, f'Assigned to {staff_user.get_full_name() or staff_user.username}.')
                except User.DoesNotExist:
                    messages.error(request, 'Staff user not found.')
            else:
                sub.assigned_to = None
                sub.save(update_fields=['assigned_to', 'updated_at'])
                messages.info(request, 'Assignment removed.')

        elif action == 'retry_notification':
            _send_retry_email(request, sub)

        return redirect('submissions:detail', pk=pk)

    staff_members = User.objects.filter(is_staff=True)
    notes = sub.internal_notes.select_related('administrator').all()
    notifications = sub.notifications.all()

    context = {
        'sub': sub,
        'candidate_app': candidate_app,
        'employer_enq': employer_enq,
        'course_adm': course_adm,
        'maint_req': maint_req,
        'staff_members': staff_members,
        'notes': notes,
        'notifications': notifications,
        'status_choices': Submission.STATUS_CHOICES,
    }
    return render(request, 'admin_custom/submission_detail.html', context)


def _send_retry_email(request, sub):
    try:
        subject = f'[Skylink Retried Alert] {sub.get_submission_type_display()} — {sub.reference_number}'
        body = (
            f"Reference Number: {sub.reference_number}\n"
            f"Division: {sub.get_division_display()}\n"
            f"Type: {sub.get_submission_type_display()}\n"
            f"Full Name: {sub.full_name}\n"
            f"Phone: {sub.phone}\n"
            f"Email: {sub.email}\n"
            f"Message: {sub.message or 'N/A'}\n"
            f"Submitted At: {sub.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
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
            status='sent',
            error_details=''
        )
        messages.success(request, f'Notification successfully re-delivered to {settings.BUSINESS_EMAIL}.')
    except Exception as e:
        NotificationLog.objects.create(
            submission=sub,
            notification_type='admin_alert',
            recipient=settings.BUSINESS_EMAIL,
            status='failed',
            error_details=str(e)
        )
        messages.error(request, f'Delivery failed: {str(e)}')


@login_required(login_url='submissions:admin_login')
@user_passes_test(is_staff_check, login_url='submissions:admin_login')
def export_csv_view(request):
    qs = Submission.objects.all()

    query = request.GET.get('q', '').strip()
    division = request.GET.get('division', '')
    status = request.GET.get('status', '')

    if query:
        qs = qs.filter(
            Q(reference_number__icontains=query) |
            Q(full_name__icontains=query) |
            Q(phone__icontains=query) |
            Q(email__icontains=query) |
            Q(company_name__icontains=query)
        )
    if division:
        qs = qs.filter(division=division)
    if status:
        qs = qs.filter(status=status)

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    filename = f'skylink_submissions_export_{timezone.now().strftime("%Y%m%d_%H%M")}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow([
        'Reference Number', 'Division', 'Submission Type', 'Status',
        'Full Name', 'Phone', 'Email', 'Company', 'Message',
        'Assigned To', 'Created Date (IST)'
    ])

    for s in qs:
        writer.writerow([
            s.reference_number,
            s.get_division_display(),
            s.get_submission_type_display(),
            s.get_status_display(),
            s.full_name,
            s.phone,
            s.email,
            s.company_name or '',
            s.message or '',
            s.assigned_to.get_full_name() if s.assigned_to else 'Unassigned',
            s.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])

    return response


@login_required(login_url='submissions:admin_login')
@user_passes_test(is_staff_check, login_url='submissions:admin_login')
def website_settings_view(request):
    return render(request, 'admin_custom/settings.html')
