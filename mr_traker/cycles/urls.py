from django.urls import path
from .views import CycleListView

urlpatterns = [
    path('', CycleListView.as_view(), name='cycle-list'),
]
