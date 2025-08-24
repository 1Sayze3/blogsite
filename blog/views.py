from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth import login
from .forms import SignUpForm

from .forms import PostForm, CommentForm, ProfileForm
from .models import Post, Comment, Profile, PostImage


def home(request):
    posts = Post.objects.select_related("author").prefetch_related("images")
    trending = Post.objects.order_by("-view_count", "-created_at")[:5]

    post_form = None
    if request.user.is_authenticated:
        if request.method == "POST":
            post_form = PostForm(request.POST, request.FILES)
            if post_form.is_valid():
                with transaction.atomic():
                    post = post_form.save(commit=False)
                    post.author = request.user
                    post.save()
                    for f in request.FILES.getlist("gallery"):
                        PostImage.objects.create(post=post, image=f)
                messages.success(request, "Post created.")
                return redirect(post.get_absolute_url())
        else:
            post_form = PostForm()

    context = {
        "posts": posts,
        "trending": trending,
        "post_form": post_form,
    }
    return render(request, "blog/home.html", context)

def post_detail(request, slug):
    post = get_object_or_404(Post.objects.select_related("author"), slug=slug)
    Post.objects.filter(pk=post.pk).update(view_count=F("view_count") + 1)

    comments = post.comments.select_related("author")
    form = CommentForm()

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "Login to comment.")
            return redirect("login")
        form = CommentForm(request.POST)
        if form.is_valid():
            Comment.objects.create(
                post=post, author=request.user, body=form.cleaned_data["body"]
            )
            messages.success(request, "Comment added.")
            return redirect(post.get_absolute_url())

    return render(request, "blog/post_detail.html", {
        "post": post,
        "comments": comments,
        "form": form,
    })


class AuthorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user or self.request.user.is_superuser

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        for f in self.request.FILES.getlist("gallery"):
            PostImage.objects.create(post=self.object, image=f)
        messages.success(self.request, "Post created.")
        return response

class PostUpdateView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    slug_field = "slug"

    def form_valid(self, form):
        response = super().form_valid(form)
        for f in self.request.FILES.getlist("gallery"):
            PostImage.objects.create(post=self.object, image=f)
        messages.success(self.request, "Post updated.")
        return response

class PostDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = Post
    slug_field = "slug"
    success_url = reverse_lazy("home")
    template_name = "blog/post_confirm_delete.html"


def profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.profile if hasattr(user, "profile") else Profile.objects.create(user=user)

    form = None
    if request.user == user:
        if request.method == "POST":
            form = ProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, "Profile updated.")
                return redirect("profile", username=user.username)
        else:
            form = ProfileForm(instance=profile)

    return render(request, "blog/profile.html", {"profile_user": user, "profile": profile, "form": form})

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})