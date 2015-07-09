from django.shortcuts import render
from django.http import HttpResponse
from django.core.urlresolvers import reverse, reverse_lazy

from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView
from django.views.generic import View

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from models import Spot, Operator, Entity, Prefix, QSO
from forms import LogUploadForm, ProfileForm

from tempfile import NamedTemporaryFile

import sys
import subprocess

class IndexView(TemplateView):
    template_name = 'dx/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['ten_recent_spots'] = Spot.objects.order_by('-id')[:10]
        return context

class RegisterView(FormView):
    template_name = 'dx/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']
        user = form.save()
        operator = Operator(user=user)
        operator.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(self.request, user)
        return super(RegisterView, self).form_valid(form)

class ProfileView(DetailView):
    model = User

    def get_object(self, queryset=None):
        obj = User.objects.get(username=self.request.user)
        return obj

class ProfileEdit(UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email']
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        obj = User.objects.get(username=self.request.user)
        return obj

class OperatorView(DetailView):
    model = Operator

    def get_object(self, queryset=None):
        q = QSO.objects.filter(operator=Operator.objects.get(user__username=self.request.user))
        print q[:10]
        obj = Operator.objects.get(user__username=self.request.user)
        return obj

class OperatorEdit(UpdateView):
    model = Operator
    fields = ['callsign',  'locator']
    success_url = reverse_lazy('operator')

    def get_object(self, queryset=None):
        obj = Operator.objects.get(user__username=self.request.user)
        return obj

class LogUploadView(FormView):
    template_name = 'dx/upload.html'
    form_class = LogUploadForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        self.handle_uploaded_file(self.request.FILES['file'])
        return super(LogUploadView, self).form_valid(form)

    def handle_uploaded_file(self, f):
        temp_file = NamedTemporaryFile(delete=False)

        with temp_file as t_f:
            for chunk in f.chunks():
                t_f.write(chunk)
            t_f.flush()

        subprocess.Popen(
            [sys.executable, 'manage.py', 'parse_log', temp_file.name, str(self.request.user)],
            # stdout=subprocess.PIPE,
            # stderr=subprocess.STDOUT,
        )
