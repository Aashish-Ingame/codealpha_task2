from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django import forms

from .models import UserProfile


class RegisterForm(UserCreationForm):
    """Registration form — username, email, password, confirm password."""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """Login form — username + password, backed by AuthenticationForm."""
    pass


class EditProfileForm(forms.ModelForm):
    """Form for editing a UserProfile's bio and avatar."""

    class Meta:
        model = UserProfile
        fields = ["bio", "avatar"]
        widgets = {
            "bio": forms.Textarea(attrs={
                "rows": 4,
                "maxlength": 500,
                "placeholder": "Tell the world a little about yourself…",
            }),
        }
