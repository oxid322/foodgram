from django.contrib.auth import get_user_model

from djoser.serializers import UserSerializer
from djoser.conf import settings
from rest_framework.serializers import ImageField, ModelSerializer

User = get_user_model()


class AvatarUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'first_name',
            'last_name',
            'avatar'
        ]
