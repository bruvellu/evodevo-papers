from django.shortcuts import render
from bot.models import Feed
from papers.models import Status


def home(request):
    feeds = Feed.objects.order_by('-source__last_change')
    statuses = Status.objects.filter(published=True).order_by('-created_at')[:5]
    context = {'feeds': feeds,
               'statuses': statuses,}
    return render(request, 'home.html', context)
