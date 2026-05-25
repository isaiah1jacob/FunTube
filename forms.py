from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Video, UserProfile, Comment

VIDEO_EXTENSIONS = {'mp4', 'webm', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'm4v'}
VIDEO_MIME_TYPES = 'video/mp4,video/webm,video/x-msvideo,video/quicktime,video/x-matroska,video/x-flv,video/x-ms-wmv,video/x-m4v'


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            pic = self.cleaned_data.get('profile_picture')
            if pic:
                user.profile.profile_picture = pic
                user.profile.save()
        return user


class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'description', 'file', 'thumbnail']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'accept': VIDEO_MIME_TYPES}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file:
            return file
        ext = file.name.split('.')[-1].lower()
        if ext not in VIDEO_EXTENSIONS:
            raise ValidationError(f'Unsupported video format "{ext}". Allowed: {", ".join(sorted(VIDEO_EXTENSIONS))}.')
        if file.size > settings.MAX_UPLOAD_SIZE:
            raise ValidationError(f'File too large ({file.size // 1024 // 1024} MB). Maximum size is {settings.MAX_UPLOAD_SIZE // 1024 // 1024} MB.')
        return file


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add a comment...'}),
        }


class VideoEditForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'description', 'thumbnail']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
        }
