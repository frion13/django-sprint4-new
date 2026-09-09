from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from blog.services import get_posts
from blog.utils import paginate

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
    posts = get_posts(
        manager=profile_user.posts,
        filter_published=request.user != profile_user,
        annotate_comments=True,
    )
    page_obj = paginate(request, posts)
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
