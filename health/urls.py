from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('log/', views.log_metrics, name='log_metrics'),
    path('insights/', views.insights, name='insights'),
    path('history/', views.history, name='history'),
    path('goals/', views.goals, name='goals'),
    path('goals/<int:pk>/delete/', views.delete_goal, name='delete_goal'),
    path('api/metrics/', views.api_metrics_json, name='api_metrics'),
]
