from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from blog.views import POSTS_BY_PAGE, get_posts, get_published_posts

from .forms import ProfileEditForm, RegistrationForm


User = get_user_model()


def registration(request):
    form = RegistrationForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('blog:index')
    return render(
        request,
        'registration/registration_form.html',
        {'form': form},
    )


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    if request.user == profile_user:
        posts = get_posts().filter(author=profile_user)
    else:
        posts = get_published_posts().filter(author=profile_user)
    page_obj = Paginator(posts, POSTS_BY_PAGE).get_page(
        request.GET.get('page')
    )
    return render(
        request,
        'blog/profile.html',
        {'profile': profile_user, 'page_obj': page_obj},
    )


@login_required
def edit_profile(request):
    form = ProfileEditForm(request.POST or None, instance=request.user)
    if form.is_valid():
        user = form.save()
        return redirect('profile', username=user.username)
    return render(request, 'registration/user.html', {'form': form})
