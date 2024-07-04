from rest_framework import serializers

from climate.models import News


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ['id', 'url', 'created_by', 'title', 'published_at', 'status'
                  'ai_questions_prompt', 'ai_questions_response', 'properties', 'location'
            ,      'tags']