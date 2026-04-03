from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    height_cm = models.FloatField(null=True, blank=True, help_text="Height in cm")
    target_weight = models.FloatField(null=True, blank=True, help_text="Target weight in kg")
    target_steps = models.PositiveIntegerField(default=10000)
    target_calories = models.PositiveIntegerField(default=2000)
    target_sleep_hours = models.FloatField(default=8.0)
    target_water_liters = models.FloatField(default=2.5)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def bmi(self):
        from health.models import HealthMetric
        latest = HealthMetric.objects.filter(user=self.user).order_by('-date').first()
        if latest and latest.weight and self.height_cm:
            height_m = self.height_cm / 100
            return round(latest.weight / (height_m ** 2), 1)
        return None

    @property
    def bmi_category(self):
        bmi = self.bmi
        if bmi is None:
            return "Unknown"
        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal"
        elif bmi < 30:
            return "Overweight"
        else:
            return "Obese"
