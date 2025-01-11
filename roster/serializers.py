# serializers.py

from rest_framework import serializers
from .models import Staff, Roster

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'

class RosterSerializer(serializers.ModelSerializer):
    staff = StaffSerializer()  # Nesting the Staff serializer

    class Meta:
        model = Roster
        fields = '__all__'