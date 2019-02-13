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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from django.views.i18n import JavaScriptCatalog
from django.urls import re_path, path, include

from base import views as base_views
from members import forms as member_forms

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='member_list'),
         name='front_page'),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(),
         {'authentication_form': member_forms.MemberAuthenticationForm},
         name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(),
         name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(),
         name='password_change_done'),
    path('password_reset/', auth_views.PasswordResetView.as_view(),
         {'password_reset_form': member_forms.MemberPasswordResetForm},
         name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
    path('medlem/', include('members.urls.member-urls')),
    path('medlemmer/', include('members.urls.members-urls')),
    path('slagverkgrupper/', include('members.urls.percussion_group-urls')),
    path('komiteer/', include('members.urls.committee-urls')),
    path('praktisk/', include('misc.urls.practical-urls')),
    path('forum/', include('forum.urls')),
    path('påmelding/', include('polls.urls')),
    path('endre-innhold/', base_views.EditableContentSave.as_view()),
    path('endre-innhold/bilde', base_views.EditableContentSaveImage.as_view()),
    path('aktiviteter/', include('activities.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
