from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from djoser.conf import settings
from rest_framework.fields import SerializerMethodField, CharField, ModelField, IntegerField
from rest_framework.serializers import ImageField, ModelSerializer, Serializer
from foodgram.models import Subcription

User = get_user_model()


class AvatarUserSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = request.user
        if Subcription.objects.filter(user=user, subscribed_to=obj).exists():
            return True
        return False

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')

        if request.path == r'/api/users/me/':
            representation.pop('is_subscribed', None)
        return representation


class SubscriptionSerializer(Serializer):
    id = SerializerMethodField()

    class Meta:
        fields = ('id',)

    def get_id(self, obj, request):

        return -1
