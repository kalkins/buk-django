"""buk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from members import forms as member_forms, views as member_views

urlpatterns = [
    url(r'^$', RedirectView.as_view(pattern_name='member_list'), name='front_page'),
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', auth_views.login, {'authentication_form': member_forms.MemberAuthenticationForm}, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^password_change/$', auth_views.password_change, name='password_change'),
    url(r'^password_change/done/$', auth_views.password_change_done, name='password_change_done'),
    url(r'^password_reset/$', auth_views.password_reset, {'password_reset_form': member_forms.MemberPasswordResetForm},
        name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
    url(r'^medlem/(?P<pk>[0-9]+)$', member_views.MemberDetail.as_view(), name='member_detail'),
    url(r'^medlemmer/$', member_views.MemberList.as_view(), {'show_all': False}, name='member_list'),
    url(r'^medlemmer/alle$', member_views.MemberList.as_view(), {'show_all': True}, name='member_list_all'),
]
