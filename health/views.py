import json
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg, Sum, Max, Min
from .models import HealthMetric, HealthGoal
from .forms import HealthMetricForm, HealthGoalForm
from accounts.models import UserProfile


def get_ai_insights(user, metrics, profile):
    """Generate AI-powered health insights based on user data."""
    insights = []
    tips = []

    if not metrics.exists():
        return [{
            'type': 'info',
            'icon': 'fa-lightbulb',
            'title': 'Get Started',
            'message': 'Log your first health metrics to get personalized AI insights!',
            'color': 'primary'
        }], []

    latest = metrics.first()
    avg_steps = metrics.aggregate(Avg('steps'))['steps__avg'] or 0
    avg_sleep = metrics.aggregate(Avg('sleep_hours'))['sleep_hours__avg'] or 0
    avg_hr = metrics.aggregate(Avg('heart_rate'))['heart_rate__avg'] or 0
    avg_water = metrics.aggregate(Avg('water_liters'))['water_liters__avg'] or 0
    avg_calories_in = metrics.aggregate(Avg('calories_intake'))['calories_intake__avg'] or 0
    avg_calories_out = metrics.aggregate(Avg('calories_burned'))['calories_burned__avg'] or 0

    target_steps = getattr(profile, 'target_steps', 10000) or 10000
    target_sleep = getattr(profile, 'target_sleep_hours', 8) or 8
    target_water = getattr(profile, 'target_water_liters', 2.5) or 2.5
    target_calories = getattr(profile, 'target_calories', 2000) or 2000

    # Steps analysis
    if avg_steps > 0:
        steps_pct = (avg_steps / target_steps) * 100
        if steps_pct >= 100:
            insights.append({
                'type': 'success', 'icon': 'fa-walking',
                'title': '🏆 Step Goal Crusher!',
                'message': f"You're averaging {int(avg_steps):,} steps/day — exceeding your {target_steps:,} goal! Keep it up.",
                'color': 'success'
            })
        elif steps_pct >= 70:
            insights.append({
                'type': 'warning', 'icon': 'fa-walking',
                'title': 'Almost There on Steps',
                'message': f"You're at {int(steps_pct)}% of your step goal. Try adding a 15-minute walk after dinner.",
                'color': 'warning'
            })
            tips.append("💡 Tip: Park farther from your destination to sneak in extra steps.")
        else:
            insights.append({
                'type': 'danger', 'icon': 'fa-walking',
                'title': 'Low Activity Detected',
                'message': f"Only {int(avg_steps):,} avg steps/day vs your {target_steps:,} goal. A sedentary lifestyle increases health risks.",
                'color': 'danger'
            })
            tips.append("💡 Set hourly reminders to stand up and walk for 5 minutes.")

    # Sleep analysis
    if avg_sleep > 0:
        if avg_sleep >= 8:
            insights.append({
                'type': 'success', 'icon': 'fa-moon',
                'title': 'Excellent Sleep Quality',
                'message': f"Averaging {avg_sleep:.1f} hrs/night. Quality sleep supports immune function, memory, and weight management.",
                'color': 'success'
            })
        elif avg_sleep >= 7:
            insights.append({
                'type': 'info', 'icon': 'fa-moon',
                'title': 'Good Sleep Pattern',
                'message': f"{avg_sleep:.1f} hrs/night average. Try to reach 8 hours for optimal recovery.",
                'color': 'info'
            })
            tips.append("💡 Avoid screens 30 minutes before bed to improve sleep quality.")
        else:
            insights.append({
                'type': 'danger', 'icon': 'fa-moon',
                'title': 'Sleep Deficit Alert',
                'message': f"Only {avg_sleep:.1f} hrs/night — below the 7-9 hour recommendation. Chronic sleep loss affects metabolism and mental health.",
                'color': 'danger'
            })
            tips.append("💡 Maintain a consistent sleep schedule, even on weekends.")

    # Heart rate analysis
    if avg_hr > 0:
        if avg_hr < 60:
            insights.append({
                'type': 'success', 'icon': 'fa-heartbeat',
                'title': 'Athletic Heart Rate',
                'message': f"Resting HR of {int(avg_hr)} bpm indicates excellent cardiovascular fitness.",
                'color': 'success'
            })
        elif avg_hr <= 80:
            insights.append({
                'type': 'info', 'icon': 'fa-heartbeat',
                'title': 'Healthy Heart Rate',
                'message': f"Resting HR of {int(avg_hr)} bpm is within the normal range (60-80 bpm).",
                'color': 'info'
            })
        else:
            insights.append({
                'type': 'warning', 'icon': 'fa-heartbeat',
                'title': 'Elevated Heart Rate',
                'message': f"Resting HR of {int(avg_hr)} bpm is above optimal. Stress, caffeine, or dehydration can elevate HR.",
                'color': 'warning'
            })
            tips.append("💡 Try 5-minute deep breathing exercises to lower resting heart rate.")

    # Water intake
    if avg_water > 0:
        if avg_water >= target_water:
            insights.append({
                'type': 'success', 'icon': 'fa-tint',
                'title': 'Well Hydrated!',
                'message': f"Averaging {avg_water:.1f}L/day — meeting your hydration goal. Great job!",
                'color': 'success'
            })
        else:
            insights.append({
                'type': 'warning', 'icon': 'fa-tint',
                'title': 'Drink More Water',
                'message': f"Only {avg_water:.1f}L/day vs your {target_water}L goal. Dehydration reduces energy and cognitive performance.",
                'color': 'warning'
            })
            tips.append("💡 Keep a water bottle at your desk and drink a glass before each meal.")

    # BMI insight
    try:
        bmi = profile.bmi
        if bmi:
            category = profile.bmi_category
            color_map = {'Normal': 'success', 'Underweight': 'warning', 'Overweight': 'warning', 'Obese': 'danger'}
            insights.append({
                'type': color_map.get(category, 'info'), 'icon': 'fa-weight',
                'title': f'BMI: {bmi} ({category})',
                'message': get_bmi_message(bmi, category),
                'color': color_map.get(category, 'info')
            })
    except Exception:
        pass

    # Calorie balance
    if avg_calories_in > 0 and avg_calories_out > 0:
        balance = avg_calories_in - avg_calories_out
        if abs(balance) < 100:
            insights.append({
                'type': 'success', 'icon': 'fa-fire',
                'title': 'Balanced Calorie Intake',
                'message': f"Your calories in vs out are nearly balanced ({int(balance):+d} avg). Perfect for weight maintenance.",
                'color': 'success'
            })
        elif balance > 500:
            insights.append({
                'type': 'warning', 'icon': 'fa-fire',
                'title': 'Calorie Surplus',
                'message': f"Consuming {int(balance)} more calories than you burn daily. This may lead to weight gain over time.",
                'color': 'warning'
            })
        elif balance < -500:
            insights.append({
                'type': 'info', 'icon': 'fa-fire',
                'title': 'Calorie Deficit',
                'message': f"Burning {abs(int(balance))} more calories than you consume. Good for weight loss if intentional.",
                'color': 'info'
            })

    # General tips
    tips.extend([
        "💡 Consistency beats intensity — small daily habits create lasting health changes.",
        "💡 Track your metrics at the same time each day for most accurate trends.",
        "💡 A 10-minute morning stretch can improve energy levels throughout the day.",
    ])

    return insights[:6], tips[:4]


def get_bmi_message(bmi, category):
    messages = {
        'Underweight': f"BMI of {bmi} suggests you may benefit from increasing caloric intake with nutrient-dense foods.",
        'Normal': f"BMI of {bmi} is in the healthy range (18.5-24.9). Maintain your current lifestyle!",
        'Overweight': f"BMI of {bmi} is slightly above normal. Moderate diet changes and exercise can help.",
        'Obese': f"BMI of {bmi} indicates obesity. Consider consulting a healthcare provider for a personalized plan.",
    }
    return messages.get(category, f"BMI: {bmi}")


@login_required
def dashboard(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)

    metrics = HealthMetric.objects.filter(user=request.user)
    recent_metrics = metrics.filter(date__gte=last_30_days).order_by('date')
    today_metric = metrics.filter(date=today).first()
    latest_metric = metrics.first()

    # Chart data (last 14 days)
    last_14 = metrics.filter(date__gte=today - timedelta(days=14)).order_by('date')
    chart_labels = [m.date.strftime('%b %d') for m in last_14]
    steps_data = [m.steps or 0 for m in last_14]
    weight_data = [m.weight or None for m in last_14]
    sleep_data = [m.sleep_hours or 0 for m in last_14]
    calories_data = [m.calories_intake or 0 for m in last_14]
    water_data = [m.water_liters or 0 for m in last_14]

    # Weekly summary
    this_week = metrics.filter(date__gte=today - timedelta(days=7))
    weekly_stats = {
        'avg_steps': int(this_week.aggregate(Avg('steps'))['steps__avg'] or 0),
        'avg_sleep': round(this_week.aggregate(Avg('sleep_hours'))['sleep_hours__avg'] or 0, 1),
        'avg_water': round(this_week.aggregate(Avg('water_liters'))['water_liters__avg'] or 0, 1),
        'avg_hr': int(this_week.aggregate(Avg('heart_rate'))['heart_rate__avg'] or 0),
        'total_calories_burned': int(this_week.aggregate(Sum('calories_burned'))['calories_burned__sum'] or 0),
    }

    # Streaks
    streak = 0
    check_date = today
    while metrics.filter(date=check_date).exists():
        streak += 1
        check_date -= timedelta(days=1)

    # Goals
    goals = HealthGoal.objects.filter(user=request.user, status='active')[:3]

    context = {
        'profile': profile,
        'today_metric': today_metric,
        'latest_metric': latest_metric,
        'weekly_stats': weekly_stats,
        'streak': streak,
        'goals': goals,
        'chart_labels': json.dumps(chart_labels),
        'steps_data': json.dumps(steps_data),
        'weight_data': json.dumps(weight_data),
        'sleep_data': json.dumps(sleep_data),
        'calories_data': json.dumps(calories_data),
        'water_data': json.dumps(water_data),
        'total_logs': metrics.count(),
        'today': today,
    }
    return render(request, 'health/dashboard.html', context)


@login_required
def log_metrics(request):
    today = timezone.now().date()
    existing = HealthMetric.objects.filter(user=request.user, date=today).first()

    if request.method == 'POST':
        form = HealthMetricForm(request.POST, instance=existing)
        if form.is_valid():
            metric = form.save(commit=False)
            metric.user = request.user
            metric.save()
            messages.success(request, '✅ Health metrics logged successfully!')
            return redirect('dashboard')
    else:
        form = HealthMetricForm(instance=existing, initial={'date': today})

    recent = HealthMetric.objects.filter(user=request.user).order_by('-date')[:7]
    return render(request, 'health/log_metrics.html', {'form': form, 'recent': recent, 'existing': existing})


@login_required
def insights(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    metrics = HealthMetric.objects.filter(
        user=request.user,
        date__gte=timezone.now().date() - timedelta(days=30)
    ).order_by('-date')

    ai_insights, tips = get_ai_insights(request.user, metrics, profile)

    # Trend data
    metrics_list = list(metrics.order_by('date'))
    trend_data = {
        'dates': [m.date.strftime('%b %d') for m in metrics_list],
        'steps': [m.steps or 0 for m in metrics_list],
        'sleep': [m.sleep_hours or 0 for m in metrics_list],
        'weight': [m.weight for m in metrics_list],
    }

    context = {
        'insights': ai_insights,
        'tips': tips,
        'profile': profile,
        'metrics_count': metrics.count(),
        'trend_data': json.dumps(trend_data),
    }
    return render(request, 'health/insights.html', context)


@login_required
def history(request):
    metrics = HealthMetric.objects.filter(user=request.user).order_by('-date')
    return render(request, 'health/history.html', {'metrics': metrics})


@login_required
def goals(request):
    user_goals = HealthGoal.objects.filter(user=request.user)
    if request.method == 'POST':
        form = HealthGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, '🎯 New goal set!')
            return redirect('goals')
    else:
        form = HealthGoalForm()
    return render(request, 'health/goals.html', {'goals': user_goals, 'form': form})


@login_required
def delete_goal(request, pk):
    goal = get_object_or_404(HealthGoal, pk=pk, user=request.user)
    goal.delete()
    messages.success(request, 'Goal removed.')
    return redirect('goals')


@login_required
def api_metrics_json(request):
    """API endpoint for chart data."""
    from django.http import JsonResponse
    days = int(request.GET.get('days', 30))
    start = timezone.now().date() - timedelta(days=days)
    metrics = HealthMetric.objects.filter(user=request.user, date__gte=start).order_by('date')
    data = [{
        'date': m.date.isoformat(),
        'steps': m.steps,
        'weight': m.weight,
        'sleep': m.sleep_hours,
        'heart_rate': m.heart_rate,
        'calories_intake': m.calories_intake,
        'calories_burned': m.calories_burned,
        'water': m.water_liters,
    } for m in metrics]
    return JsonResponse({'data': data})
