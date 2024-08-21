from rest_framework import serializers
from .models import GenerateUniqueTrackingNumber

class GenerateTrackingNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenerateUniqueTrackingNumber
        fields = "__all__"
        
        