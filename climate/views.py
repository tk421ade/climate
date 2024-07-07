from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from climate.models import News
from climate.serializers import NewsSerializer

PAGE_SIZE = 10


def index(request):
    page_number = request.GET.get('p', 1)
    #news = News.objects.filter(status='NEW').order_by('-created')
    news = News.objects.filter(status='NEW').order_by('-created')
    paginator = Paginator(news, PAGE_SIZE)
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'news': page, 'page_number': page_number})


def go(request, news_id: int):
    news = News.objects.get(id=news_id)
    news.hits = news.hits + 1
    news.save()
    return HttpResponseRedirect(news.url)


class NewsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        url = request.query_params.get('url', None)
        news = News.objects.filter(url=url)
        serializer = NewsSerializer(news, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = NewsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)