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
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

from base import views as base_views
from members import forms as member_forms, views as member_views
from misc import views as misc_views

from polls import views as poll_views

urlpatterns = [
    url(r'^$', RedirectView.as_view(pattern_name='member_list'),
        name='front_page'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', auth_views.login,
        {'authentication_form': member_forms.MemberAuthenticationForm},
        name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^password_change/$', auth_views.password_change,
        name='password_change'),
    url(r'^password_change/done/$', auth_views.password_change_done,
        name='password_change_done'),
    url(r'^password_reset/$', auth_views.password_reset,
        {'password_reset_form': member_forms.MemberPasswordResetForm},
        name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done,
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete,
        name='password_reset_complete'),
    url(r'^medlem/', include('members.urls.member-urls')),
    url(r'^medlemmer/', include('members.urls.members-urls')),
    url(r'^slagverkgrupper/', include('members.urls.percussion_group-urls')),
    url(r'^praktisk/', include('misc.urls.practical-urls')),
    url(r'^forum/', include('forum.urls')),
    url(r'^påmelding/', include('polls.urls')),
    url(r'^endre-innhold/$', base_views.EditableContentSave.as_view()),
    url(r'^endre-innhold/bilde$', base_views.EditableContentSaveImage.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
