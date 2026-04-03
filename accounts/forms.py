from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('age', 'gender', 'height_cm', 'target_weight',
                  'target_steps', 'target_calories', 'target_sleep_hours',
                  'target_water_liters', 'avatar')
        widgets = {
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 120}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'height_cm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'target_weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'target_steps': forms.NumberInput(attrs={'class': 'form-control'}),
            'target_calories': forms.NumberInput(attrs={'class': 'form-control'}),
            'target_sleep_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'target_water_liters': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }
