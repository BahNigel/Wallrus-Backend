from django.shortcuts import render

# Create your views here.

from notifications.serializer import *
from notifications.models import *
from users.models import CustomUser

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

class UserNotificationsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        notifications = UserNotifications.objects.filter(user=request.user).order_by('-created_at')
        serializer = UserNotificationsSerializer(instance=notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class MarkAllAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = UserNotifications.objects.filter(user=request.user,is_read = False)
        for notification in notifications:
            notification.is_read = True
            notification.save()
        return Response({'msg':'Success'}, status=status.HTTP_200_OK)