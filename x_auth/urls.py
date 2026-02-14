
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.twitter_login, name='twitter_login'),
    path('callback/', views.twitter_callback, name='twitter_callback'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('delete/<int:pk>/', views.delete_tweet, name='delete_tweet'),
    path('edit/<int:pk>/', views.edit_tweet, name='edit_tweet'),
]