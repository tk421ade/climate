from rest_framework import serializers

from climate.models import News


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        # 'status',
        fields = ['id', 'title', 'summary', 'description', 'url',  'ai_prompt', 'ai_response',
                  'ai_questions_prompt', 'ai_questions_response', 'properties', 'location',
                  'tags', 'created_by', 'published_at']