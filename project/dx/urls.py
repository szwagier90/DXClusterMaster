from django.conf.urls import patterns, url

from django.contrib.auth.views import login
from django.contrib.auth.decorators import login_required

from dx import views

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^upload/$', views.LogUploadView.as_view(), name='upload'),
    url(r'^filter/$', views.FilterDetailView.as_view(), name='filter'),
    url(r'^filter/edit/$', views.FilterEditView.as_view(), name='filter_edit'),
    url(r'^operator/$', views.OperatorView.as_view(), name='operator'),
    url(r'^operator/edit/', views.OperatorEdit.as_view(), name='operator_edit'),
    url(r'^accounts/register/', views.RegisterView.as_view(), name='register'),
    url(r'^accounts/profile/$', views.ProfileView.as_view(), name='profile'),
    url(r'^accounts/profile/edit/$', views.ProfileEdit.as_view(), name='profile_edit'),
)

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^accounts/login/$', 'login', {'template_name': 'dx/login.html'}, name='login'),
    url(r'^accounts/logout/$', 'logout', {'next_page': '/'}, name='logout'),
)
