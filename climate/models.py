from django.contrib.postgres.fields.array import ArrayField
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class News(models.Model):
    DRAFT = 'DRAFT'
    NEW = 'NEW'
    PUBLISHED = 'PUBLISHED'
    DISCARDED = 'DISCARDED'
    ERROR = 'ERROR'
    STATUS_CHOICES = [
        (DRAFT, 'DRAFT'),
        (NEW, 'NEW'),
        (PUBLISHED, 'PUBLISHED'),
        (DISCARDED, 'DISCARDED'),
        (ERROR, 'ERROR')
    ]
    title = models.CharField(max_length=200)
    summary = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    url = models.URLField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="NEW")
    ai_prompt = models.TextField(null=True, blank=True)
    ai_response = models.TextField(null=True, blank=True)
    ai_questions_prompt = models.TextField(null=True, blank=True)
    ai_questions_response = models.TextField(null=True, blank=True)
    tags = ArrayField(models.TextField(), size=5, null=True, blank=True)
    properties = ArrayField(models.TextField(), null=True, blank=True)
    location = ArrayField(models.TextField(), null=True, blank=True)
    created = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    published_at = models.DateTimeField(null=True, blank=True)
    hits = models.IntegerField(default=0)
    #votes_anonymous = models.IntegerField()
    #votes

    class Meta:
        verbose_name = "News"
        verbose_name_plural = "News"

    def __str__(self):
        return f"{self.title} by {self.created_by}"
