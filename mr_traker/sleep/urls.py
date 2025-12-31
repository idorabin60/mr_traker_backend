from django.urls import path
from .views import SleepListView, LatestSleepView

urlpatterns = [
    path('', SleepListView.as_view(), name='sleep-list'),
    path('latest/', LatestSleepView.as_view(), name='sleep-latest'),
]
