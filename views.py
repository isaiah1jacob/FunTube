from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import models as db_models
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Video, UserProfile, Comment
from .forms import VideoUploadForm, RegisterForm, UserProfileForm, CommentForm, VideoEditForm


class HomeView(ListView):
    model = Video
    template_name = 'videos/home.html'
    context_object_name = 'videos'
    paginate_by = 12

    def get_queryset(self):
        q = self.request.GET.get('q', '').strip()
        if q:
            return Video.objects.filter(
                db_models.Q(title__icontains=q) | db_models.Q(description__icontains=q)
            )
        return Video.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '').strip()
        return context


class VideoDetailView(DetailView):
    model = Video
    template_name = 'videos/video_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        Video.objects.filter(pk=self.object.pk).update(views=db_models.F('views') + 1)
        self.object.refresh_from_db()
        context['user_video_count'] = Video.objects.filter(uploaded_by=self.object.uploaded_by).count()
        context['comments'] = self.object.comments.select_related('user').all()
        context['comment_form'] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user.is_authenticated:
            return redirect('login')
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.video = self.object
            comment.user = request.user
            comment.save()
        return redirect('video_detail', pk=self.object.pk)


class UploadVideoView(LoginRequiredMixin, CreateView):
    model = Video
    form_class = VideoUploadForm
    template_name = 'videos/upload.html'
    success_url = '/'

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        return super().form_valid(form)


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'videos/register.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')


class ProfileView(DetailView):
    model = User
    template_name = 'videos/profile.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_videos'] = Video.objects.filter(uploaded_by=self.object)
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'videos/edit_profile.html'

    def get_object(self):
        return self.request.user.profile

    def get_success_url(self):
        return reverse('profile', kwargs={'username': self.request.user.username})


class DashboardView(LoginRequiredMixin, ListView):
    model = Video
    template_name = 'videos/dashboard.html'
    context_object_name = 'videos'
    paginate_by = 12

    def get_queryset(self):
        return Video.objects.filter(uploaded_by=self.request.user)


class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        video = self.get_object()
        return self.request.user == video.uploaded_by


class EditVideoView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Video
    form_class = VideoEditForm
    template_name = 'videos/edit_video.html'

    def get_success_url(self):
        return reverse('video_detail', kwargs={'pk': self.object.pk})


class DeleteVideoView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Video
    template_name = 'videos/delete_video.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['video_title'] = self.object.title
        return context


@require_POST
@login_required
def like_toggle(request, pk):
    video = get_object_or_404(Video, pk=pk)
    if request.user in video.likes.all():
        video.likes.remove(request.user)
        liked = False
    else:
        video.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'count': video.likes.count()})
