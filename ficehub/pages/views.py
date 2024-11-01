from django.shortcuts import render
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from .forms import PostSearchForm, CommentForm
from bestiaria.settings import ENCRYPTION_KEY
from pages.auth import require_guest, require_login
from pages.models import Post
from django.db.models import Q
from django.views.generic import TemplateView, ListView
from django.core.mail import send_mail
from datetime import datetime
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth import logout


def main_page(request):
    posts = Post.objects.all().order_by('-created_at')
    form = PostSearchForm(request.GET or None)
    if form.is_valid():
        category = form.cleaned_data.get('category')
        hashtags = form.cleaned_data.get('hashtags')
        search_text = form.cleaned_data.get('search_text')

        # Filter by category if selected
        if category:
            posts = posts.filter(category=category)

        # Filter by selected hashtags
        if hashtags:
            posts = posts.filter(hashtags__in=hashtags).distinct()

        # Perform search across name, text, and hashtags
        if search_text:
            posts = posts.filter(
                Q(name__icontains=search_text) |
                Q(text__icontains=search_text) |
                Q(hashtags__name__icontains=search_text)
            ).distinct()
    posts = form.cleaned_data.get('posts')

    return render(request, )

@login_required
def user_admin_page(request):
    user = request.user
    is_admin = user.is_staff
    users = User.objects.all() if is_admin else None
    posts = Post.objects.filter(author=user) if not is_admin else None

    context = {
        'user': user,
        'is_admin': is_admin,
        'users': users,
        'posts': posts,
    }
    return render(request, 'admin_page.html', context)


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    comments = Comment.objects.filter(post=post)

    context = {
        'post': post,
        'comments': comments,
    }
    return render(request, 'post_detail.html', context)


def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category)

    context = {
        'category': category,
        'posts': posts,
    }
    return render(request, 'category_posts.html', context)

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts_count = Post.objects.filter(category=category).count()

    context = {
        'category': category,
        'posts_count': posts_count,
    }
    return render(request, 'category_detail.html', context)

@login_required
def group_detail(request):
    user_group = request.user.group  # Assumes 'group' field in User
    members = user_group.members.all() if user_group else []

    context = {
        'group': user_group,
        'members': members,
        'message': "You are not in any student group!" if not user_group else None,
    }
    return render(request, 'group_detail.html', context)


@login_required
def profile(request, slug):
    user = get_object_or_404(User, slug=slug)
    if request.user == user:
        return redirect('user_admin_page')
    posts_count = user.posts.count()
    comments_count = user.comments.count()

    context = {
        'profile_user': user,
        'posts_count': posts_count,
        'comments_count': comments_count,
    }
    return render(request, 'profile.html', context)

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after registration
            return redirect('profile_update')  # Redirect to profile update page
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('main_page')
# Create your views here.
