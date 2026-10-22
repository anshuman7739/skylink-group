from django import forms

PROPERTY_CHOICES = [
    ('', 'Select Property Classification *'),
    ('residential_apartment', 'Residential — Apartment / Flat'),
    ('residential_house', 'Residential — Independent House / Bungalow'),
    ('commercial_office', 'Commercial — Office / Corporate Workplace'),
    ('commercial_shop', 'Commercial — Retail Shop / Showroom / Restaurant'),
    ('commercial_warehouse', 'Commercial — Warehouse / Factory / Workshop'),
    ('institutional', 'Institutional — School / College / Hospital / Clinic'),
    ('other', 'Other Commercial / Residential Property'),
]

SERVICE_CHOICES = [
    ('', 'Select Service Category *'),
    ('electrical', 'Electrical Repair, Wiring & Distribution Board'),
    ('ac_hvac', 'AC / HVAC Repair, Gas Charging & Installation'),
    ('plumbing', 'Plumbing, Leakage Repair & Sanitary Fitting'),
    ('handyman', 'General Handyman, Carpentry & Minor Civil Works'),
    ('facility_management', 'Annual Maintenance Contract (AMC) & Facility Services'),
    ('multiple', 'Multiple / Full Property Renovation Maintenance'),
]

ALLOWED_ATTACHMENT_TYPES = [
    'image/jpeg', 'image/png', 'image/webp', 'image/heic',
    'application/pdf'
]


class MaintenanceRequestForm(forms.Form):
    name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Your Full Name *',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-maintenance focus:border-maintenance outline-none transition'
        })
    )
    phone = forms.CharField(
        max_length=25,
        widget=forms.TextInput(attrs={
            'placeholder': 'Active Contact / Mobile Number *',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-maintenance focus:border-maintenance outline-none transition'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email Address *',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-maintenance focus:border-maintenance outline-none transition'
        })
    )
    property_type = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-maintenance focus:border-maintenance outline-none transition bg-white'
        })
    )
    service_category = forms.ChoiceField(
        choices=SERVICE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-maintenance focus:border-maintenance outline-none transition bg-white'
        })
    )
    location = forms.CharField(
        max_length=300,
        widget=forms.TextInput(attrs={
            'placeholder': 'Complete Property Address, Landmark & City *',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-maintenance focus:border-maintenance outline-none transition'
        })
    )
    problem_description = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Describe the breakdown, issue, or scope of work in detail... *',
            'rows': 4,
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-maintenance focus:border-maintenance outline-none transition'
        })
    )
    preferred_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-maintenance focus:border-maintenance outline-none transition bg-white'
        })
    )
    attachment = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-maintenance/10 file:text-maintenance hover:file:bg-maintenance/20 cursor-pointer',
            'accept': 'image/*,.pdf'
        })
    )
    website = forms.CharField(required=False, widget=forms.HiddenInput())

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        digits = ''.join(filter(str.isdigit, phone))
        if len(digits) < 10:
            raise forms.ValidationError('Please enter a valid phone number with at least 10 digits.')
        return phone

    def clean_attachment(self):
        file = self.cleaned_data.get('attachment')
        if file:
            if file.size > 8 * 1024 * 1024:
                raise forms.ValidationError('Attachment size must be under 8 MB.')
            if file.content_type not in ALLOWED_ATTACHMENT_TYPES:
                raise forms.ValidationError('Accepted formats are JPG, PNG, WEBP, or PDF.')
        return file

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError('Spam detected.')
        return ''
