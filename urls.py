from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('upload/', views.UploadVideoView.as_view(), name='upload'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('video/<int:pk>/', views.VideoDetailView.as_view(), name='video_detail'),
    path('video/<int:pk>/edit/', views.EditVideoView.as_view(), name='edit_video'),
    path('video/<int:pk>/delete/', views.DeleteVideoView.as_view(), name='delete_video'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='videos/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/<slug:username>/', views.ProfileView.as_view(), name='profile'),
    path('profile/<slug:username>/edit/', views.EditProfileView.as_view(), name='edit_profile'),
    path('video/<int:pk>/like/', views.like_toggle, name='like_toggle'),
]
