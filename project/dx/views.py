from django.shortcuts import render
from django.http import HttpResponse
from django.core.urlresolvers import reverse

from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views.generic import View

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login

from models import Spot

class IndexView(TemplateView):
    template_name = 'dx/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['last_five_spots'] = Spot.objects.order_by('time')[:5]
        return context

class RegisterView(FormView):
    template_name = 'dx/register.html'
    form_class = UserCreationForm
    success_url = '/'#reverse('index', current_app='dx')

    def form_valid(self, form):
        print form.cleaned_data['username']
        print form.cleaned_data['password1']
        user = form.save()
        user = authenticate(username=user.username, password=user.password)
        if user is not None:
            if user.is_active:
                login(request, user)
        return super(RegisterView, self).form_valid(form)
