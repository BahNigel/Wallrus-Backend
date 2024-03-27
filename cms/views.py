from urllib import response
from django.shortcuts import render
from rest_framework.views import APIView, Response, status

from .models import Section, Content
from .serializers import ContentSerializer

# Create your views here.

class ContentView(APIView):

    def get(self, request, section):
        try:
            section = Section.objects.get(name=section)
            contents = Content.objects.filter(section = section).order_by('sequence_number')
            serializer = ContentSerializer(instance=contents, many=True)
            return Response(data= {'header':section.header, 'items':serializer.data})
        except Exception as e:
            print(e)
            return Response(data={'msg':'Invalid section'}, status=status.HTTP_400_BAD_REQUEST)

