from django import forms

DIVISION_CHOICES = [
    ('', 'Select Division'),
    ('staffing', 'Skylink Staffing Solutions Pvt. Ltd.'),
    ('academy', 'Skylink Skill Academy'),
    ('maintenance', 'Skylink Maintenance Services'),
    ('general', 'General / Group Corporate Enquiry'),
]

ENQUIRY_TYPE_CHOICES = [
    ('', 'Select Enquiry Type'),
    ('information', 'General Information / Questions'),
    ('service_enquiry', 'Service / Business Enquiry'),
    ('partnership', 'Strategic Partnership / Agency Tie-up'),
    ('recruitment_tieup', 'Corporate Recruitment Tie-up'),
    ('complaint', 'Feedback or Grievance'),
    ('other', 'Other Inquiries'),
]


class GeneralEnquiryForm(forms.Form):
    name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Your Full Name *',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-navy focus:border-navy outline-none transition'
        })
    )
    phone = forms.CharField(
        max_length=25,
        widget=forms.TextInput(attrs={
            'placeholder': 'Phone Number (e.g. +91 90455 85073) *',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-navy focus:border-navy outline-none transition'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Official / Personal Email *',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-navy focus:border-navy outline-none transition'
        })
    )
    company_name = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Company / Organisation Name (optional)',
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-navy focus:border-navy outline-none transition'
        })
    )
    division = forms.ChoiceField(
        choices=DIVISION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-navy focus:border-navy outline-none transition bg-white'
        })
    )
    enquiry_type = forms.ChoiceField(
        choices=ENQUIRY_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-navy focus:border-navy outline-none transition bg-white'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Describe your requirements or enquiry in detail... *',
            'rows': 4,
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-navy focus:border-navy outline-none transition'
        })
    )
    consent = forms.BooleanField(
        required=True,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-navy rounded border-gray-300 focus:ring-navy'
        })
    )
    # Honeypot spam prevention field
    website = forms.CharField(required=False, widget=forms.HiddenInput())

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        digits = ''.join(filter(str.isdigit, phone))
        if len(digits) < 10:
            raise forms.ValidationError('Please enter a valid phone number with at least 10 digits.')
        return phone

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError('Spam submission detected.')
        return ''

    def clean_division(self):
        d = self.cleaned_data.get('division')
        if not d:
            raise forms.ValidationError('Please select a business division.')
        return d

    def clean_enquiry_type(self):
        t = self.cleaned_data.get('enquiry_type')
        if not t:
            raise forms.ValidationError('Please select an enquiry type.')
        return t
