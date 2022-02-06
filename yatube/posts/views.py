from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from yatube.settings import POSTS_PER_SITE, RATING_DELTA

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User, Rating, SetRating


def pagination(request, all_post):
    paginator = Paginator(all_post, POSTS_PER_SITE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def rating_change(request, author, delta):
    user = get_object_or_404(User, username=author)
    if request.user != author:
        SetRating.objects.get_or_create(user=request.user, author=author)

    if Rating.objects.filter(author=user).exists():
        rating = Rating.objects.get(author=user)
        rating.rat += delta * RATING_DELTA
        rating.save()
    else:
        rating = Rating.objects.create(rat=0, author=user)
        rating.rat += delta * RATING_DELTA
        rating.save()


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.all()
    rating = Rating.objects.all()
    page_obj = pagination(request, posts)
    context = {
        'page_obj': page_obj,
        'rating': rating,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = pagination(request, posts)
    context = {
        'group': group,
        'page_obj': page_obj,
    }

    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    rating = Rating.objects.all()
    page_obj = pagination(request, posts)
    following = (request.user.is_authenticated
                 and Follow.objects.filter(user=request.user, author=author)
                 .exists())
    if SetRating.objects.filter(user=request.user, author=author).exists():
        vote = False
    else:
        vote = True
    context = {
        'page_obj': page_obj,
        'author': author,
        'posts': posts,
        'following': following,
        'rating': rating,
        'vote': vote,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    form = CommentForm()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None
                    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)
    groups = Group.objects.all()
    return render(request, 'posts/create_post.html', {'form': form,
                                                      'groups': groups})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    groups = Group.objects.all()
    author = post.author
    if request.user != author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'post': post,
        'groups': groups,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    rating = Rating.objects.all()
    page_obj = pagination(request, posts)
    context = {
        'page_obj': page_obj,
        'rating': rating,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.get(user=request.user, author=author)
    if request.user != author:
        follow.delete()
    return redirect('posts:profile', username=username)


def rating_inc(request, author):
    if not SetRating.objects.filter(user=request.user, author=author).exists():
        rating_change(request, author, 1)
    return redirect('posts:profile', username=author)


def rating_dec(request, author):
    if not SetRating.objects.filter(user=request.user, author=author).exists():
        rating_change(request, author, -1)
    return redirect('posts:profile', username=author)
