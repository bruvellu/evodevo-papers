from django.shortcuts import render
from feeds.models import Source
from papers.models import Status


def home(request):
    sources = Source.objects.all()
    statuses = Status.objects.filter(published=True).order_by('-created_at')[:5]
    context = {'sources': sources,
               'statuses': statuses,}
    return render(request, 'home.html', context)
