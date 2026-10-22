from django import forms

JOB_ROLE_CHOICES = [
    ('', 'Select Job Role / Trade *'),
    ('Electrician', 'Electrician (Commercial / Industrial / Domestic)'),
    ('AC / HVAC Technician', 'AC & HVAC Technician / Refrigeration Mechanic'),
    ('Plumber', 'Plumber / Pipe Fitter'),
    ('Welder & Fabricator', 'Welder (MIG/TIG/ARC) & Fabricator'),
    ('Civil & Construction Worker', 'Civil & Construction Skilled Worker'),
    ('Carpenter & Mason', 'Carpenter / Mason / Tile Fitter'),
    ('Painter & Finisher', 'Painter / Wall Finisher'),
    ('Industrial Housekeeping', 'Industrial Housekeeping & Cleaning Specialist'),
    ('Security Guard', 'Security Guard / Supervisor'),
    ('Heavy / Light Driver', 'Heavy / Light Commercial Vehicle Driver'),
    ('Chef / Cook', 'Commercial Cook / Kitchen Staff'),
    ('Healthcare / Nurse', 'Nurse / Healthcare Assistant / Caregiver'),
    ('IT & Technical Support', 'IT Support / Systems Technician'),
    ('Accountant & Office Admin', 'Accountant / Office Coordinator'),
    ('Field Supervisor', 'Site / Field Operations Supervisor'),
    ('Other Skilled / Unskilled', 'Other Skilled or General Labor'),
]

EXPERIENCE_CHOICES = [
    ('', 'Select Years of Experience *'),
    ('fresher', 'Fresher (0 years / Training completed)'),
    ('less_1', 'Less than 1 year'),
    ('1_3', '1 to 3 years'),
    ('3_5', '3 to 5 years'),
    ('5_10', '5 to 10 years (Experienced)'),
    ('10_plus', '10+ years (Master Craftsman / Specialist)'),
]

ALLOWED_RESUME_TYPES = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
]


class JobApplicationForm(forms.Form):
    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Full Name (as per Aadhaar / Passport) *',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-navy focus:border-navy outline-none transition'
        })
    )
    phone = forms.CharField(
        max_length=25,
        widget=forms.TextInput(attrs={
            'placeholder': 'Mobile Number (WhatsApp preferred) *',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-navy focus:border-navy outline-none transition'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email Address *',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-navy focus:border-navy outline-none transition'
        })
    )
    city_state = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Current City & State (e.g. Gopalganj, Bihar) *',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-navy focus:border-navy outline-none transition'
        })
    )
    job_role = forms.ChoiceField(
        choices=JOB_ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-navy focus:border-navy outline-none transition bg-white'
        })
    )
    experience = forms.ChoiceField(
        choices=EXPERIENCE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-navy focus:border-navy outline-none transition bg-white'
        })
    )
    preferred_location = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Preferred Work Location (e.g. Gulf/Middle East, India, Pan-India)',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-navy focus:border-navy outline-none transition'
        })
    )
    skills = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'List key skills, tools operated, certifications or previous companies... *',
            'rows': 3,
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-navy focus:border-navy outline-none transition'
        })
    )
    resume = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-navy/10 file:text-navy hover:file:bg-navy/20 cursor-pointer',
            'accept': '.pdf,.doc,.docx'
        })
    )
    privacy_consent = forms.BooleanField(
        required=True,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-navy rounded border-gray-300 focus:ring-navy'})
    )
    # Honeypot spam prevention
    website = forms.CharField(required=False, widget=forms.HiddenInput())

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        digits = ''.join(filter(str.isdigit, phone))
        if len(digits) < 10:
            raise forms.ValidationError('Please enter a valid phone number with at least 10 digits.')
        return phone

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            if resume.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Resume file must be under 5 MB in size.')
            if resume.content_type not in ALLOWED_RESUME_TYPES:
                raise forms.ValidationError('Only PDF (.pdf) or Word document (.doc, .docx) formats are accepted.')
        return resume

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError('Spam detected.')
        return ''


WORKER_COUNT_CHOICES = [
    ('', 'Select Number of Workers Required *'),
    ('1-5 workers', '1 to 5 Personnel'),
    ('6-15 workers', '6 to 15 Personnel'),
    ('16-50 workers', '16 to 50 Personnel (Medium Batch)'),
    ('51-100 workers', '51 to 100 Personnel (Large Deployment)'),
    ('100+ workers', '100+ Turnkey Workforce Deployment'),
]


class EmployerEnquiryForm(forms.Form):
    contact_person = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Contact Person Name & Designation *',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-navy focus:border-navy outline-none transition'
        })
    )
    company_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Company / Enterprise Legal Name *',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-navy focus:border-navy outline-none transition'
        })
    )
    phone = forms.CharField(
        max_length=25,
        widget=forms.TextInput(attrs={
            'placeholder': 'Official Phone / Mobile *',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-navy focus:border-navy outline-none transition'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Corporate / HR Email Address *',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-navy focus:border-navy outline-none transition'
        })
    )
    industry = forms.CharField(
        required=False,
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Industry / Sector (e.g. Oil & Gas, Construction, Manufacturing, Facilities)',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-navy focus:border-navy outline-none transition'
        })
    )
    job_roles_required = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'List required job roles and quantities (e.g. 20 Electricians, 10 HVAC Techs, 5 Site Foremen) *',
            'rows': 3,
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-navy focus:border-navy outline-none transition'
        })
    )
    worker_count = forms.ChoiceField(
        choices=WORKER_COUNT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-navy focus:border-navy outline-none transition bg-white'
        })
    )
    skills_required = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Specific skills, licenses, trade test requirements, or minimum experience needed...',
            'rows': 2,
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-navy focus:border-navy outline-none transition'
        })
    )
    work_location = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Work Site Location (City/Country, e.g. Dubai UAE / Saudi Arabia / Gujarat India) *',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-navy focus:border-navy outline-none transition'
        })
    )
    expected_joining = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-navy focus:border-navy outline-none transition bg-white'
        })
    )
    requirements = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Additional requirements (accommodation, transport, visa sponsorship, contract duration)...',
            'rows': 3,
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-navy focus:border-navy outline-none transition'
        })
    )
    website = forms.CharField(required=False, widget=forms.HiddenInput())

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        digits = ''.join(filter(str.isdigit, phone))
        if len(digits) < 10:
            raise forms.ValidationError('Please enter a valid phone number with at least 10 digits.')
        return phone

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError('Spam detected.')
        return ''
