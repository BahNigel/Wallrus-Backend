from rest_framework import serializers

from .models import Section, Content

class ContentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Content
        fields = '__all__'