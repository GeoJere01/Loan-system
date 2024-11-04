from django.urls import include, path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns =[
    path('', views.home, name="home"),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.login_page, name="login"),
    path('loan/', views.loans, name="loans"),
    path('register/', views.register_user, name="register"),
    path('user/<int:id>/profile', views.user_details, name="user_details"),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
]