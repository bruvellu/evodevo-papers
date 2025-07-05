from django.shortcuts import render
from .models import Feed, Post


def home(request):
    feeds = Feed.objects.order_by("-source__last_change")
    posts = Post.objects.order_by("-created")[:5]
    context = {
        "feeds": feeds,
        "posts": posts,
    }
    return render(request, "home.html", context)


def about(request):
    context = {}
    return render(request, "about.html", context)


def feeds(request):
    feeds = Feed.objects.order_by("name")
    context = {"feeds": feeds}
    return render(request, "feeds.html", context)


def feed(request, id):
    feed = Feed.objects.get(id=id)
    entries = feed.source.posts.order_by("-created")
    context = {
        "feed": feed,
        "entries": entries,
    }
    return render(request, "feed.html", context)


def posts(request):
    posts = Post.objects.order_by("-created")
    context = {"posts": posts}
    return render(request, "posts.html", context)


def post(request, id):
    post = Post.objects.get(id=id)
    context = {"post": post}
    return render(request, "post.html", context)
