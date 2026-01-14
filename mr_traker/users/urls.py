from django.urls import path
from .views import RegisterView, LoginView, MyAthletesView, PrivacyPolicyView, WhoopCallbackView, WhoopWebhookView, AthleteDetailView

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('trainer/athletes/', MyAthletesView.as_view(), name='trainer-athletes'),
    path('trainer/athletes/<int:pk>/', AthleteDetailView.as_view(), name='athlete-detail'),
    
    # WHOOP Integration
    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy-policy'),
    path('whoop/callback/', WhoopCallbackView.as_view(), name='whoop-callback'),
    path('whoop/webhook/', WhoopWebhookView.as_view(), name='whoop-webhook'),
]
