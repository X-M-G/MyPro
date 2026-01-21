from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CreditTransaction, FAQ

User = get_user_model()

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'credits', 'phone_number', 'invitation_code', 'is_staff', 'is_superuser']
        read_only_fields = ['credits', 'invitation_code']

class CreditTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditTransaction
        fields = ['id', 'amount', 'balance_after', 'description', 'timestamp']
        read_only_fields = ['id', 'timestamp', 'balance_after']
