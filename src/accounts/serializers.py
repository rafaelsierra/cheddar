from django.contrib.auth.models import User
from django.conf import settings

from rest_framework import serializers


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'last_login', 'date_joined')
        read_only_fields = ('username', 'last_login', 'date_joined')


class NewAccountSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def validate_email(self, value):
        if User.objects.filter(email=value.lower()).count() > 0:
            raise serializers.ValidationError('E-mail not available')
        return value

    def create(self, validated_data):
        user = User(
            username=validated_data['username'].lower(),
            email=validated_data['email'].lower()
        )
        user.set_password(validated_data['password'])
        user.is_active = settings.CHEDDAR_DEFAULT_USER_ACTIVE_STATUS
        user.save()
        return user
