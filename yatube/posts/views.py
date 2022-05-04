from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm
from .utils import paginator


def index(request):
    post_list = Post.objects.select_related('author').all()
    page_obj = paginator(post_list, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group)
    page_obj = paginator(post_list, request)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)

    post_list = author.posts.all()
    page_obj = paginator(post_list, request)

    follow = request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author=author).exists()
    context = {
        'page_obj': page_obj,
        'author': author,
        'following': follow,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_list = post.author.posts.all()
    amount_of_posts = post_list.count()
    text30 = post.text[:30]
    form = CommentForm(request.POST or None)
    comment_list = post.comments.all()

    context = {
        'post': post,
        'form': form,
        'comments': comment_list,
        'amount_of_posts': amount_of_posts,
        'text30': text30,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    is_edit = False
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author.username)

    context = {
        'form': form,
        'is_edit': is_edit,
    }
    return render(request, 'posts/post_create.html', context)


@login_required
def post_edit(request, post_id):
    user = request.user.id
    post = get_object_or_404(Post, pk=post_id)
    author = post.author.id
    is_edit = True
    if user != author:
        return redirect('posts:post_detail', post_id=post.pk)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.pk)
    context = {
        'post': post,
        'form': form,
        'is_edit': is_edit,
    }
    return render(request, 'posts/post_create.html', context)


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

    comment_list = post.comments.all()

    context = {
        'form_comment': form,
        'comments': comment_list,
    }
    return render(request, 'posts/post_create.html', context)


@login_required
def follow_index(request):
    user = get_object_or_404(User, username=request.user)
    post_list = Post.objects.filter(author__following__user=user)
    page_obj = paginator(post_list, request)
    context = {
        'user': user,
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow_index.html', context)


@login_required
def profile_follow(request, username):
    follower = request.user
    author = get_object_or_404(User, username=username)
    if follower.id != author.id:
        Follow.objects.get_or_create(
            user=follower,
            author=author
        )
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    folower = request.user
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(
        user=folower,
        author=author
    ).delete()
    return redirect('posts:follow_index')
