from django import forms
from .models import Post, Comment, Profile, PostImage
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class PostForm(forms.ModelForm):
    gallery = forms.FileField(
        widget=MultiFileInput(attrs={"multiple": True}),
        required=False,
        help_text="Optional: upload multiple images"
    )
    class Meta:
        model = Post
        fields = ["title", "content", "featured_image"]

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {"body": forms.Textarea(attrs={"rows": 3})}

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["avatar", "bio", "website", "location"]

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]