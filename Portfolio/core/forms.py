from django import forms
from .models import ServiceBooking, ContactMessage

TIME_CHOICES = [('', 'Select Time')] + [
    (f"{h % 24:02d}:{m:02d}", f"{12 if h % 12 == 0 else h % 12:d}:{m:02d} {'AM' if h < 12 or h == 24 else 'PM'}")
    for h in range(9, 25)
    for m in (0, 30)
    if not (h == 24 and m == 30)
]

class ServiceBookingForm(forms.ModelForm):
    preferred_time = forms.ChoiceField(
        choices=TIME_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full bg-black border border-white/20 rounded-lg px-4 py-1.5 text-white focus:outline-none focus:border-primary transition text-sm cursor-pointer appearance-none',
        })
    )
    
    class Meta:
        model = ServiceBooking
        fields = ['name', 'phone', 'email', 'preferred_date', 'preferred_time', 'additional_message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full bg-white/5 border border-white/20 rounded-lg px-4 py-1.5 text-white placeholder:text-white focus:outline-none focus:border-primary transition text-sm',
                'placeholder': 'Your Full Name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full bg-white/5 border border-white/20 rounded-lg px-4 py-1.5 text-white placeholder:text-white focus:outline-none focus:border-primary transition text-sm',
                'placeholder': 'Your Phone Number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full bg-white/5 border border-white/20 rounded-lg px-4 py-1.5 text-white placeholder:text-white focus:outline-none focus:border-primary transition text-sm',
                'placeholder': 'Your Email Address'
            }),
            'preferred_date': forms.DateInput(attrs={
                'class': 'w-full bg-white/5 border border-white/20 rounded-lg px-4 py-1.5 text-white placeholder:text-white focus:outline-none focus:border-primary transition text-sm',
                'type': 'date',
                'style': 'color-scheme: dark;' 
            }),
            'additional_message': forms.Textarea(attrs={
                'class': 'w-full bg-white/5 border border-white/20 rounded-lg px-4 py-1.5 text-white placeholder:text-white focus:outline-none focus:border-primary transition text-sm',
                'placeholder': 'Additional Message',
                'rows': 2
            }),
        }

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full bg-white/5 border border-white/20 rounded-lg px-4 py-1.5 text-white placeholder:text-white focus:outline-none focus:border-primary transition text-sm',
                'placeholder': 'Your Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full bg-white/5 border border-white/20 rounded-lg px-4 py-1.5 text-white placeholder:text-white focus:outline-none focus:border-primary transition text-sm',
                'placeholder': 'Your Email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full bg-white/5 border border-white/20 rounded-lg px-4 py-1.5 text-white placeholder:text-white focus:outline-none focus:border-primary transition text-sm',
                'placeholder': 'Your Phone Number'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'w-full bg-white/5 border border-white/20 rounded-lg px-4 py-1.5 text-white placeholder:text-white focus:outline-none focus:border-primary transition text-sm',
                'placeholder': 'Subject'
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full bg-white/5 border border-white/20 rounded-lg px-4 py-2 text-white placeholder:text-white focus:outline-none focus:border-primary transition text-sm',
                'placeholder': 'Your Message',
                'rows': 4
            }),
        }
