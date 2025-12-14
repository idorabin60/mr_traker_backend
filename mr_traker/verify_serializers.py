
import os
import django
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mr_traker.settings")
django.setup()

from users.models import User, AthleteProfile
from medical_history.models import MedicalHistory, MedicalHistoryNote
from medical_history.serializers import MedicalHistorySerializer

def verify():
    # clean up
    User.objects.filter(username="test_serializer").delete()
    
    # Setup data
    user = User.objects.create_user(username="test_serializer", password="password")
    athlete, _ = AthleteProfile.objects.get_or_create(user=user)
    
    history = MedicalHistory.objects.create(
        athlete=athlete,
        title="Flu",
        description="High fever"
    )
    
    MedicalHistoryNote.objects.create(
        medical_history=history,
        role='HUMAN',
        description="Fever started yesterday"
    )
    MedicalHistoryNote.objects.create(
        medical_history=history,
        role='AI',
        description="Recommend rest and fluids"
    )
    
    # Test Serializer
    serializer = MedicalHistorySerializer(history)
    data = serializer.data
    
    print("Serialized Data:")
    print(data)
    
    assert data['title'] == "Flu"
    assert len(data['notes']) == 2
    assert data['notes'][0]['role'] in ['HUMAN', 'AI']
    
    print("Verification Successful!")

if __name__ == "__main__":
    verify()
