from django.shortcuts import render
from .models import Feed, Post


def home(request):
    feeds = Feed.objects.order_by('-source__last_change')
    posts = Post.objects.filter(published=True).order_by('-created_at')[:5]
    context = {'feeds': feeds,
               'posts': posts,}
    return render(request, 'home.html', context)


def feeds(request):
    feeds = Feed.objects.order_by('name')
    context = {'feeds': feeds}
    return render(request, 'feeds.html', context)
