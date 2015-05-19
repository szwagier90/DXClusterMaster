from django.conf.urls import patterns, url

from django.contrib.auth.views import login

from django.contrib.auth.decorators import login_required

from dx import views

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^upload/$', views.LogUploadView.as_view(), name='upload'),
    url(r'^accounts/register/', views.RegisterView.as_view(), name='register'),
)

urlpatterns += patterns('django.contrib.auth.views',
	url(r'^accounts/login/$', 'login', {'template_name': 'dx/login.html'}, name='login'),
	url(r'^accounts/logout/$', 'logout', name='logout'),
)