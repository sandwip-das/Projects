from django import forms
from django.contrib.auth import authenticate
from .models import User

class UserRegistrationForm(forms.ModelForm):
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 rounded-lg bg-gray-50 border border-gray-300 focus:border-primary focus:ring-2 focus:ring-indigo-200 outline-none transition',
        'placeholder': 'Phone Number (Optional)'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 rounded-lg bg-gray-50 border border-gray-300 focus:border-primary focus:ring-2 focus:ring-indigo-200 outline-none transition',
        'placeholder': 'Enter your password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 rounded-lg bg-gray-50 border border-gray-300 focus:border-primary focus:ring-2 focus:ring-indigo-200 outline-none transition',
        'placeholder': 'Confirm your password'
    }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg bg-gray-50 border border-gray-300 focus:border-primary focus:ring-2 focus:ring-indigo-200 outline-none transition',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg bg-gray-50 border border-gray-300 focus:border-primary focus:ring-2 focus:ring-indigo-200 outline-none transition',
                'placeholder': 'Last Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg bg-gray-50 border border-gray-300 focus:border-primary focus:ring-2 focus:ring-indigo-200 outline-none transition',
                'placeholder': 'name@company.com'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'date_of_birth', 'gender', 'profile_image']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-primary focus:border-primary'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-primary focus:border-primary'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-primary focus:border-primary'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-primary focus:border-primary', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-primary focus:border-primary'}),
            'profile_image': forms.URLInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-primary focus:border-primary'}),
        }


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-3 rounded-lg bg-gray-50 border border-gray-300 focus:border-primary focus:ring-2 focus:ring-indigo-200 outline-none transition',
        'placeholder': 'name@company.com'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 rounded-lg bg-gray-50 border border-gray-300 focus:border-primary focus:ring-2 focus:ring-indigo-200 outline-none transition',
        'placeholder': 'Enter your password'
    }))
