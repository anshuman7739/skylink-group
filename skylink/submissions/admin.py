import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    Submission, CandidateApplication, EmployerEnquiry,
    CourseAdmission, MaintenanceRequest, NotificationLog, InternalNote
)


def export_submissions_csv(modeladmin, request, queryset):
    if not request.user.is_staff:
        return HttpResponse('Unauthorized', status=403)
    response = HttpResponse(content_type='text/csv')
    filename = f'skylink_submissions_{timezone.now().strftime("%Y%m%d_%H%M")}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow([
        'Reference Number', 'Division', 'Submission Type', 'Status',
        'Full Name', 'Phone', 'Email', 'Company', 'Message', 'Created At'
    ])
    for s in queryset:
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
            s.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])
    return response

export_submissions_csv.short_description = 'Export selected submissions as CSV'


class InternalNoteInline(admin.TabularInline):
    model = InternalNote
    extra = 1
    readonly_fields = ('administrator', 'created_at')

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, InternalNote) and not instance.pk:
                instance.administrator = request.user
            instance.save()
        formset.save_m2m()


class NotificationLogInline(admin.TabularInline):
    model = NotificationLog
    extra = 0
    readonly_fields = ('notification_type', 'recipient', 'status', 'provider_message_id', 'error_details', 'created_at')
    can_delete = False


class CandidateApplicationInline(admin.StackedInline):
    model = CandidateApplication
    extra = 0
    readonly_fields = ('resume_download',)

    def resume_download(self, obj):
        if obj and obj.resume:
            return format_html('<a href="{}" target="_blank" class="button" style="color:#2563EB;font-weight:600;">📄 Download Resume ({})</a>', obj.resume.url, obj.resume.name)
        return 'No resume uploaded'
    resume_download.short_description = 'Resume Document'


class EmployerEnquiryInline(admin.StackedInline):
    model = EmployerEnquiry
    extra = 0


class CourseAdmissionInline(admin.StackedInline):
    model = CourseAdmission
    extra = 0


class MaintenanceRequestInline(admin.StackedInline):
    model = MaintenanceRequest
    extra = 0
    readonly_fields = ('attachment_preview',)

    def attachment_preview(self, obj):
        if obj and obj.attachment:
            return format_html('<a href="{}" target="_blank" class="button" style="color:#D97706;font-weight:600;">📎 View Attachment ({})</a>', obj.attachment.url, obj.attachment.name)
        return 'No attachment uploaded'
    attachment_preview.short_description = 'Damage/Site Attachment'


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = [
        'reference_number', 'full_name', 'phone', 'division_badge',
        'type_badge', 'status_badge', 'email_status', 'created_at'
    ]
    list_filter = ['division', 'submission_type', 'status', 'created_at']
    search_fields = ['reference_number', 'full_name', 'phone', 'email', 'company_name']
    readonly_fields = ['id', 'reference_number', 'created_at', 'updated_at']
    list_per_page = 25
    date_hierarchy = 'created_at'
    actions = [export_submissions_csv]

    fieldsets = (
        ('Identifiers & Status', {
            'fields': ('reference_number', 'status', 'division', 'submission_type', 'assigned_to', 'source_page')
        }),
        ('Contact Information', {
            'fields': ('full_name', 'phone', 'email', 'company_name')
        }),
        ('Visitor Message', {
            'fields': ('message',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_inlines(self, request, obj):
        inlines = [InternalNoteInline, NotificationLogInline]
        if obj:
            if obj.submission_type == 'job_application':
                inlines.insert(0, CandidateApplicationInline)
            elif obj.submission_type == 'employer_enquiry':
                inlines.insert(0, EmployerEnquiryInline)
            elif obj.submission_type == 'course_admission':
                inlines.insert(0, CourseAdmissionInline)
            elif obj.submission_type == 'maintenance_request':
                inlines.insert(0, MaintenanceRequestInline)
        return inlines

    def division_badge(self, obj):
        c = obj.get_division_badge_color()
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            c, obj.get_division_display()
        )
    division_badge.short_description = 'Division'

    def type_badge(self, obj):
        return obj.get_submission_type_display()
    type_badge.short_description = 'Submission Type'

    def status_badge(self, obj):
        c = obj.get_status_color()
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            c, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def email_status(self, obj):
        logs = obj.notifications.all()
        if not logs.exists():
            return format_html('<span style="color:#6B7280;">No Log</span>')
        latest = logs.first()
        if latest.status == 'sent':
            return format_html('<span style="color:#16A34A;font-weight:700;">✓ Delivered</span>')
        elif latest.status == 'failed':
            return format_html('<span style="color:#DC2626;font-weight:700;" title="{}">✗ Failed</span>', latest.error_details)
        return format_html('<span style="color:#D97706;">Pending</span>')
    email_status.short_description = 'Notification'


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['submission', 'notification_type', 'recipient', 'status', 'created_at']
    list_filter = ['status', 'notification_type']
    search_fields = ['submission__reference_number', 'recipient']
    readonly_fields = ['submission', 'notification_type', 'recipient', 'status', 'provider_message_id', 'error_details', 'created_at']


@admin.register(InternalNote)
class InternalNoteAdmin(admin.ModelAdmin):
    list_display = ['submission', 'administrator', 'created_at']
    readonly_fields = ['created_at']
    search_fields = ['submission__reference_number', 'note']
