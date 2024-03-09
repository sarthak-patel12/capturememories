"""
URL configuration for marriage_photography project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from media.views import register_eventuser,login_eventuser,subuser_home,upload_media,view_media,delete_media,resend_otp_s
from home.views import *
from users.views import login_user,logout_user,register_user,user_home,delete_user,resend_otp
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',home,name="home"),
    path('index',register_user,name="index"),
    path('admin/', admin.site.urls),
    path('register_eventuser',register_eventuser,name="register_eventuser"),
    path('login_eventuser',login_eventuser,name="login_eventuser"),
    path('login_user',login_user,name="login_user"),
    path('logout_user',logout_user, name ='logout_user'),
    path('user_home',user_home,name="user_home"),
    path('delete_user/<int:user_id>/<str:flag>',delete_user,name="delete_user"),
    path('subuser_home',subuser_home,name="subuser_home"),
    path('upload_media',upload_media,name="upload_media"),
    path('view_media', view_media, name='view_media'),
    path('delete_media/<int:media_id>/', delete_media, name='delete_media'),
    path('resend_otp', resend_otp, name='resend_otp'),
    path('resend_otp_s', resend_otp_s, name='resend_otp_s')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
