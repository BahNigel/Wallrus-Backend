from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from users.models import CustomUser
from invite.models import Invite

class InviteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        req_user = CustomUser.objects.get(email=request.user)
        try:
            referral_code = Invite.objects.get(user=req_user).referral_code
            return Response({"referral_code": f"{referral_code}"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"Error": "User not found in Invite Friend!"}, status=status.HTTP_404_NOT_FOUND)