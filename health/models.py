from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class HealthMetric(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='metrics')
    date = models.DateField(default=timezone.now)
    steps = models.PositiveIntegerField(null=True, blank=True, help_text="Steps walked")
    calories_burned = models.PositiveIntegerField(null=True, blank=True, help_text="Calories burned")
    calories_intake = models.PositiveIntegerField(null=True, blank=True, help_text="Calories consumed")
    weight = models.FloatField(null=True, blank=True, help_text="Weight in kg")
    heart_rate = models.PositiveIntegerField(null=True, blank=True, help_text="Resting heart rate (bpm)")
    sleep_hours = models.FloatField(null=True, blank=True, help_text="Hours of sleep")
    water_liters = models.FloatField(null=True, blank=True, help_text="Water intake in liters")
    notes = models.TextField(blank=True, help_text="Optional notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.date}"

    @property
    def steps_goal_pct(self):
        try:
            target = self.user.profile.target_steps
            if self.steps and target:
                return min(round((self.steps / target) * 100), 100)
        except Exception:
            pass
        return 0

    @property
    def sleep_quality(self):
        if self.sleep_hours is None:
            return "No data"
        if self.sleep_hours >= 8:
            return "Excellent"
        elif self.sleep_hours >= 7:
            return "Good"
        elif self.sleep_hours >= 6:
            return "Fair"
        else:
            return "Poor"

    @property
    def heart_rate_zone(self):
        if self.heart_rate is None:
            return "No data"
        if self.heart_rate < 60:
            return "Athlete"
        elif self.heart_rate < 70:
            return "Excellent"
        elif self.heart_rate < 80:
            return "Good"
        elif self.heart_rate < 90:
            return "Average"
        else:
            return "High"


class HealthGoal(models.Model):
    GOAL_TYPES = [
        ('weight_loss', 'Weight Loss'),
        ('weight_gain', 'Weight Gain'),
        ('fitness', 'Improve Fitness'),
        ('sleep', 'Better Sleep'),
        ('nutrition', 'Better Nutrition'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    target_value = models.FloatField(null=True, blank=True)
    current_value = models.FloatField(null=True, blank=True)
    start_date = models.DateField(default=timezone.now)
    target_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    @property
    def progress_pct(self):
        if self.target_value and self.current_value:
            return min(round((self.current_value / self.target_value) * 100), 100)
        return 0
