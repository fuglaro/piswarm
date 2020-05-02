"""authenticator URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.contrib.auth.decorators import login_required
from django.urls import path, include

from authenticator import views

urlpatterns = [
    # Log in to the admin page via allauth
    path('auth/admin/login/', login_required(admin.site.login)),
    path('auth/admin/', admin.site.urls),

    # Allauth based session login
    path('auth/accounts/', include('allauth.urls')),

    # Retrieve api token from session login
    path('auth/token/login/', login_required(views.token_login)),

    # Expire api tokens
    path('auth/token/logout/', views.token_logout),

    # Retrieve the username from an api token login or session login
    path('auth/user/', views.user),

]