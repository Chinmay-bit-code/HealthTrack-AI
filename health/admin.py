from django.contrib import admin
from .models import HealthMetric, HealthGoal


@admin.register(HealthMetric)
class HealthMetricAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'steps', 'weight', 'heart_rate', 'sleep_hours', 'water_liters')
    list_filter = ('date', 'user')
    search_fields = ('user__username',)
    date_hierarchy = 'date'


@admin.register(HealthGoal)
class HealthGoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'goal_type', 'status', 'target_date')
    list_filter = ('status', 'goal_type')
