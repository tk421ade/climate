from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render

from climate.models import News

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
