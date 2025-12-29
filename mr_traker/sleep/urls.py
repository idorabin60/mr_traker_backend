from django.urls import path
from .views import SleepListView

urlpatterns = [
    path('', SleepListView.as_view(), name='sleep-list'),
]
