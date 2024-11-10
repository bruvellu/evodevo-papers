from django.shortcuts import render
from bot.models import Feed, Post


def home(request):
    feeds = Feed.objects.order_by('-source__last_change')
    posts = Post.objects.filter(published=True).order_by('-created_at')[:5]
    context = {'feeds': feeds,
               'posts': posts,}
    return render(request, 'home.html', context)
