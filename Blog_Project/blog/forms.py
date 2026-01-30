from django import forms
from django.contrib.auth.models import User
from .models import Profile, Post, Comment, Tag

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio', 'mobile_number', 'educational_qualifications', 'interested_subjects', 'profession', 'current_city', 'country']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'educational_qualifications': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your latest earned degree'}),
            'interested_subjects': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'eg, Physics, IT, etc..'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),
            'profession': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Profession'}),
            'current_city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Current City'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
        }

class PostForm(forms.ModelForm):
    tag_str = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter tags separated by commas (e.g. Technology, Python, Web)'}),
        label="Tags"
    )
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'featured_image', 'category', 'status'] # Status kept for hidden input
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter post title...'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'id': 'post-content', 'placeholder': 'Write your post content here...'}),
            'featured_image': forms.FileInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.HiddenInput(), # Hidden, controlled by buttons
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['tag_str'].initial = ", ".join([t.name for t in self.instance.tags.all()])

    def save(self, commit=True):
        post = super().save(commit=False)
        if commit:
            post.save()
            post.tags.clear()
            tag_names = [t.strip() for t in self.cleaned_data['tag_str'].split(',') if t.strip()]
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                post.tags.add(tag)
        return post

class CommentForm(forms.ModelForm):
    parent_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Write a comment...'}),
        }

class ContactForm(forms.Form):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    mobile_number = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Description'}))
