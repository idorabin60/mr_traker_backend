from django.urls import path
from .views import RecoveryListView

urlpatterns = [
    path('', RecoveryListView.as_view(), name='recovery-list'),
]
