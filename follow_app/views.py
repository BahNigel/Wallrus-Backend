from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from users.models import CustomUser, Artist, Interior_Decorator
from notifications.models import UserNotifications

class FollowArtistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(sefl, request):
        user_unique_id = request.data['user_unique_id']

        try: 
            custom_user = CustomUser.objects.get(Unique_id=user_unique_id)
        except Exception as e:
            return Response({"details": "The user does not exist or wrong Unique Id."}, status=status.HTTP_404_NOT_FOUND)

        if custom_user.is_active == False:
            return Response({"details": "The user is not verified."}, status=status.HTTP_401_UNAUTHORIZED)
        if custom_user.type != 1:
            return Response({"details": "The user is not a artist."}, status=status.HTTP_406_NOT_ACCEPTABLE)

        followers = Artist.objects.get(user=custom_user).followers.all().count()

        return Response({"No. of followers are ": followers}, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        user_unique_id = request.data['user_unique_id']

        try: 
            custom_user = CustomUser.objects.get(Unique_id=user_unique_id)
        except Exception as e:
            return Response({"details": "The user does not exist or wrong Unique Id."}, status=status.HTTP_404_NOT_FOUND)

        if custom_user.is_active == False:
            return Response({"details": "The user is not verified."}, status=status.HTTP_401_UNAUTHORIZED)
        if custom_user.type != 1:
            return Response({"details": "The user is not a artist."}, status=status.HTTP_406_NOT_ACCEPTABLE)

        artist = Artist.objects.get(user=custom_user)
        decorator = Interior_Decorator.objects.get(user=user)
        nt_ins = UserNotifications(user=custom_user,creator=request.user, notification_type='follower', text=f"{request.user.first_name} {request.user.last_name} followed you.")
        nt_ins.save()
        
        artist.followers.add(decorator)
        return Response({"details": "A new follower added successfully."}, status=status.HTTP_201_CREATED)

    def put(self, request):
        user = request.user
        user_unique_id = request.data['user_unique_id']

        try: 
            custom_user = CustomUser.objects.get(Unique_id=user_unique_id)
        except Exception as e:
            return Response({"details": "The user does not exist or wrong Unique Id."}, status=status.HTTP_404_NOT_FOUND)

        if custom_user.is_active == False:
            return Response({"details": "The user is not verified."}, status=status.HTTP_401_UNAUTHORIZED)
        if custom_user.type != 1:
            return Response({"details": "The user is not a artist."}, status=status.HTTP_406_NOT_ACCEPTABLE)

        artist = Artist.objects.get(user=custom_user)
        decorator = Interior_Decorator.objects.get(user=user)
        
        artist.followers.remove(decorator)

        return Response({"details": "The decorator has been removed from the Artist followers list."}, status=status.HTTP_200_OK)