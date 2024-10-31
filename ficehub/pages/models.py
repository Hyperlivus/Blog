from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from django.dispatch import receiver
import markdown


# Create your models here.
class Group(models.Model):
    name = models.CharField(max_length=10, unique=True)
    def __str__(self):
       return f"{self.name}"


class User(AbstractUser):
    username = models.CharField(max_length=50, unique=True)
    fullname = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    birthdate = models.DateField(null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="posts", blank=True)
    email = models.EmailField(unique=True)
    telegram = models.CharField(max_length=50, blank=True)
    password = models.CharField(max_length=128)
    is_blocked = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    redirect_url = models.URLField(blank=True, null=True)
    rating = models.FloatField(default=0.0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


    def update_rating(self):
        posts = self.posts.all()
        comments = self.comments.all()
        if posts.exists():
            total_rating = sum(post.rating for post in posts) + sum(comment.rating for comment in comments)
            self.rating = total_rating / (posts.count() + comments.count())
        else:
            self.rating = 0
        self.save()
    def __str__(self):
       return f"{self.username}"

    def get_absolute_url(self):
        return reverse('user_detail', kwargs={'slug': self.slug})


class Category(models.Model):
    name = models.CharField(max_length=30, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.CharField(max_length=100)  # Increased length for flexibility
    redirect_url = models.URLField(blank=True, null=True)  # If this stores a URL

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})


class Hashtag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="posts")
    hashtags = models.ManyToManyField(Hashtag, related_name="posts", blank=True)
    text = models.TextField()  # Markdown text
    image = models.ImageField(upload_to="post_images/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rating = models.IntegerField(default=0)
    views = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        if not self.slug:  # Generate slug only if it's not set
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1

            # Ensure the slug is unique by adding a suffix if needed
            while super().objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def increase_views(self):
        self.views += 1
        self.save()

    def render_markdown(self):
        return markdown.markdown(self.text)

    def change_rating(self, value):
        """Change the rating of the post by a specified value."""
        self.rating += value
        self.save()
        self.user.update_rating()

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'slug': self.slug})


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f"Comment by {self.author} on {self.post.title}"

    def render_markdown(self):
        return markdown.markdown(self.text)

    def change_rating(self, value):
        """Change the rating of the post by a specified value."""
        self.rating += value
        self.save()
        self.user.update_rating()


@receiver(post_save, sender=Post)
def update_user_rating_on_post_save(sender, instance, **kwargs):
    instance.user.update_rating()

@receiver(post_delete, sender=Post)
def update_user_rating_on_post_delete(sender, instance, **kwargs):
    instance.user.update_rating()