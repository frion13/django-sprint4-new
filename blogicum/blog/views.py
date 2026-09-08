from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post

POSTS_BY_PAGE = 10


def get_posts():
    """Вернуть публикации вместе со связанными объектами и агрегатами."""
    return Post.objects.select_related(
        'author', 'category', 'location'
    ).annotate(
        comment_count=Count('comments'),
    ).order_by('-pub_date')


def get_published_posts():
    """Вернуть опубликованные посты с данными связанных моделей."""
    return get_posts().filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True,
    )


def index(request):
    page_obj = Paginator(get_published_posts(), POSTS_BY_PAGE).get_page(
        request.GET.get('page')
    )

    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, post_id):
    post = get_object_or_404(
        get_posts(),
        id=post_id,
    )
    is_available = (
        post.is_published
        and post.pub_date <= timezone.now()
        and post.category is not None
        and post.category.is_published
    )
    if not is_available and request.user != post.author:
        raise Http404
    comments = post.comments.select_related('author')
    context = {
        'post': post,
        'comments': comments,
        'form': CommentForm(),
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )

    posts_qs = get_published_posts().filter(
        category=category,
    )

    page_obj = Paginator(posts_qs, POSTS_BY_PAGE).get_page(
        request.GET.get('page')
    )
    context = {'category': category, 'page_obj': page_obj}
    return render(request, 'blog/category.html', context)


@login_required
def create_post(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post.id)
    form = PostForm(
        request.POST or None,
        request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post.id)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post.id)
    form = PostForm(instance=post)
    if request.method == 'POST':
        username = post.author.username
        post.delete()
        return redirect('profile', username=username)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect('blog:post_detail', post_id=post.id)
    context = {
        'post': post,
        'comments': post.comments.select_related('author'),
        'form': form,
    }
    return render(request, 'blog/detail.html', context)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(
        Comment,
        id=comment_id,
        post_id=post_id,
    )
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    context = {'comment': comment, 'form': form}
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(
        Comment,
        id=comment_id,
        post_id=post_id,
    )
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', {'comment': comment})
