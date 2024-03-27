from dataclasses import fields
from notifications.models import *
from rest_framework import serializers

from api.serializers import SearchUserSerializer

class UserNotificationsSerializer(serializers.ModelSerializer):
    creator = SearchUserSerializer()
    class Meta:
        model = UserNotifications
        fields = "__all__"