from django import forms

COURSE_CHOICES = [
    ('', 'Select Vocational Course *'),
    ('electrician', 'Electrician Training (3 Months — Basic to Industrial)'),
    ('ac_refrigeration', 'AC & Refrigeration Technician (3 Months — Inverter & Commercial)'),
    ('plumbing', 'Plumbing & Pipe Fitting (2 Months — Sanitary & High-Pressure)'),
    ('safety', 'Safety / HSE Training (1 Month — International Safety Standards)'),
    ('electrician_adv', 'Advanced Electrician & Control Panels (6 Months)'),
    ('ac_hvac_adv', 'Advanced AC, HVAC & Chiller Plant Management (6 Months)'),
]

BATCH_CHOICES = [
    ('', 'Select Preferred Batch Timing *'),
    ('morning', 'Morning Batch (8:00 AM – 12:00 PM)'),
    ('afternoon', 'Afternoon Batch (12:00 PM – 4:00 PM)'),
    ('evening', 'Evening Batch (4:00 PM – 8:00 PM)'),
    ('weekend', 'Weekend Batch (Saturday & Sunday Intensive)'),
]

EDUCATION_CHOICES = [
    ('', 'Highest Education Level (Optional)'),
    ('below_10', 'Below Class 10 (Practical Learner)'),
    ('class_10', 'Class 10th (Matriculation Pass)'),
    ('class_12', 'Class 12th (Intermediate / +2)'),
    ('diploma', 'ITI / Polytechnic Diploma Holder'),
    ('graduate', 'Graduate / Degree Holder'),
    ('other', 'Other Qualification'),
]


class CourseAdmissionForm(forms.Form):
    name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Student / Candidate Full Name *',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-academy focus:border-academy outline-none transition'
        })
    )
    phone = forms.CharField(
        max_length=25,
        widget=forms.TextInput(attrs={
            'placeholder': 'Contact Mobile / WhatsApp Number *',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-academy focus:border-academy outline-none transition'
        })
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email Address (optional)',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-academy focus:border-academy outline-none transition'
        })
    )
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'City / Town / Village & District *',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-academy focus:border-academy outline-none transition'
        })
    )
    course = forms.ChoiceField(
        choices=COURSE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-academy focus:border-academy outline-none transition bg-white'
        })
    )
    preferred_batch = forms.ChoiceField(
        choices=BATCH_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-academy focus:border-academy outline-none transition bg-white'
        })
    )
    education_level = forms.ChoiceField(
        required=False,
        choices=EDUCATION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-academy focus:border-academy outline-none transition bg-white'
        })
    )
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Any prior technical experience, hostel requirement, or queries...',
            'rows': 3,
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-academy focus:border-academy outline-none transition'
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
