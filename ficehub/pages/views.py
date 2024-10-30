from django.shortcuts import render
"""
from pages.models import Category
from pages.models import Post
from pages.models import Plan
from page.models import Tasks
from page.models import SocialMedia
from page.models import Author
from page.models import Comment
from django.core.paginator import Paginator
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
"""
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from .forms import PostForm, CommentForm
from bestiaria.settings import ENCRYPTION_KEY
from page.auth import require_guest, require_login
from page.models import Message, User, Playlist, Artist
from django.db.models import Q
from django.views.generic import TemplateView, ListView
from django.core.mail import send_mail
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.conf import settings

def post(request, cat_name, post_name):
    def post_detail(request, slug):
        post = get_object_or_404(Post, slug=slug)
        post.increase_views()  # Increase view count
        return render(request, "blog/post_detail.html", {"post": post})
    category = get_object_or_404(Category, slugstart=cat_name)
    post = get_object_or_404(Post, slug=post_name)
    related = Post.objects.filter(category=category).order_by('-date')[0:3]
    return render(request, 'post.html', {'category':category,  'post':post, 'categories': Category.objects.all(),
                   'plans': Plan.objects.all(), 'socmedia': SocialMedia.objects.all(), 'tasks': Tasks.objects.all(),
                   "authors": Author.objects.all(), 'html':f'{post.slug}.html', 'recent':related})


# Create your views here.
