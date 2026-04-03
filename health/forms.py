from django import forms
from .models import HealthMetric, HealthGoal
from django.utils import timezone


class HealthMetricForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        initial=timezone.now
    )

    class Meta:
        model = HealthMetric
        fields = ('date', 'steps', 'calories_burned', 'calories_intake',
                  'weight', 'heart_rate', 'sleep_hours', 'water_liters', 'notes')
        widgets = {
            'steps': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 8500', 'min': 0}),
            'calories_burned': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 350', 'min': 0}),
            'calories_intake': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 1800', 'min': 0}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 70.5', 'step': '0.1', 'min': 0}),
            'heart_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 72', 'min': 30, 'max': 250}),
            'sleep_hours': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 7.5', 'step': '0.5', 'min': 0, 'max': 24}),
            'water_liters': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2.5', 'step': '0.1', 'min': 0}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'How are you feeling today?'}),
        }


class HealthGoalForm(forms.ModelForm):
    class Meta:
        model = HealthGoal
        fields = ('goal_type', 'title', 'description', 'target_value', 'current_value', 'target_date')
        widgets = {
            'goal_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Lose 5kg by June'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'target_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'current_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'target_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
