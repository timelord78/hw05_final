from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page})


def group_post(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    group_paginator = Paginator(posts, settings.PAGES)
    page_number = request.GET.get('page')
    page = group_paginator.get_page(page_number)
    context = {'page': page, 'group': group, 'posts': posts}
    return render(request, 'group.html', context)


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'new_post.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:index')


def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.all()
    post_count = author.posts.all().count()
    profile_paginator = Paginator(author_posts, settings.PAGES)
    page_number = request.GET.get('page')
    page = profile_paginator.get_page(page_number)
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author).exists()
    else:
        following = False
    context = {'author': author,
               'author_posts': author_posts,
               'page': page,
               'post_count': post_count,
               'following': following}
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    post = get_object_or_404(
        Post, author__username=username, id=post_id)
    author = post.author
    post_count = author.posts.all().count()
    form = CommentForm()
    comments = post.comments.filter(post=post)
    context = {'author': author,
               'author_post': post,
               'post_count': post_count,
               'form': form,
               'comments': comments,
               'post': post}
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if request.user != post.author:
        return redirect('posts:post', username, post_id)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post', username, post_id)
    context = {'form': form, 'post': post}
    return render(request, 'new_post.html', context)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post', username, post_id)


@login_required
def follow_index(request):
    username = Follow.objects.filter(author__following__user=request.user)
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, settings.PAGES)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {'page': page, 'username': username})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user_signed = Follow.objects.filter(
        user=request.user,
        author=author)
    if request.user != author:
        if user_signed.exists() is False:
            Follow.objects.create(
                user=request.user,
                author=author
            )
        return redirect('posts:profile', username=username)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user_signed = Follow.objects.filter(
        user=request.user,
        author=author)
    if user_signed.exists():
        user_signed.delete()
        return redirect('posts:profile', username=username)
