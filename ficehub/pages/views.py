from django.shortcuts import render
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from mypy.dmypy.client import request
from django.contrib.auth import login
from .forms import PostSearchForm, PostForm, PostUpdateForm, CommentForm, RegistrationForm
from bestiaria.settings import ENCRYPTION_KEY
from pages.auth import require_guest, require_login
from pages.models import Post, User, Comment, Category, Image
from django.db.models import Q
from django.views.generic import TemplateView, ListView
from django.core.mail import send_mail
from datetime import datetime
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth import logout


def main_page(request):
    form = PostSearchForm(request.GET or None)
    sort_option = request.GET.get('sort', 'newest')
    if sort_option == 'views':
        posts = Post.objects.all().order_by('-views')
    elif sort_option == 'rating':
        posts = Post.objects.all().order_by('-rating')
    else:
        posts = Post.objects.all().order_by('-created_at')

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
    context = {
        "posts": posts,
        "form": form,
        "sort_option": sort_option,
    }
    return render(request, context)

@login_required
def user_admin_page(request):
    user = request.user
    is_admin = user.is_staff
    users = User.objects.all() if is_admin else None
    posts = Post.objects.filter(author=user)

    context = {
        'user': user,
        'is_admin': is_admin,
        'users': users,
        'posts': posts,
    }
    return render(request, 'admin_page.html', context)


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            # Handle multiple image uploads
            images = request.FILES.getlist('images')
            for image_file in images:
                Image.objects.create(post=post, image=image_file)

            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})


@login_required
def edit_post(request, slug):
    post = get_object_or_404(Post, slug=slug)

    # Ensure that only the author can edit
    if post.author != request.user:
        return redirect('post_detail', slug=slug)

    if request.method == 'POST':
        form = PostUpdateForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostUpdateForm(instance=post)

    return render(request, 'edit_post.html', {'form': form, 'post': post})

@login_required
def delete_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if post.author != request.user and not request.user.is_staff:
        return redirect('post_detail', slug=slug)
    else:
        post.delete()
        previous_page = request.META.get('HTTP_REFERER')
        if previous_page:
            return redirect(previous_page)
        else:
            return redirect('/')

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    comments = Comment.objects.filter(post=post)
    if request.method == 'POST':
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.save()
            return redirect('post_detail', slug=post.slug)
    else:
        form = CommentForm()
    context = {
        'post': post,
        'comments': comments,
        'form': form,
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
        return redirect('admin')
    posts_count = user.posts.count()
    comments_count = user.comments.count()

    context = {
        'profile_user': user,
        'posts_count': posts_count,
        'comments_count': comments_count,
    }
    return render(request, 'profile.html', context)

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful.")
                return redirect('/')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('main_page')
# Create your views here.
