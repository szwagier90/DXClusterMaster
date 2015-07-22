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

from models import Spot, Operator, Entity, Band, Prefix, QSO, FileProcessingProgress, Filter
from forms import LogUploadForm, ProfileEditForm

from tempfile import NamedTemporaryFile

import sys
import subprocess

from drafts import colors

class IndexView(TemplateView):
    template_name = 'dx/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        try:
            ten_recent_spots = Spot.objects.order_by('-id')[:10]
            operator = Operator.objects.get(user__username=self.request.user)

            try:
                progress = FileProcessingProgress.objects.get(operator=operator)

                context['progress'] = progress
            except FileProcessingProgress.DoesNotExist:
                context['progress'] = "NULL"

        except Operator.DoesNotExist:
            context['progress'] = 'NoOP'
            spots = [{'spot': spot, 'interesting': False} for spot in ten_recent_spots]
        else:
            spots = [self.filter_spot(spot, operator) for spot in ten_recent_spots]

        for spot in spots:
            if spot['interesting'] == True:
                print colors.green(spot['spot'])
            else:
                print colors.red(spot['spot'])

        context['ten_recent_spots'] = spots

        return context

    def filter_spot(self, spot, operator):
        filtered_spot = {}

        frequency = spot.frequency / 1000

        try:
            band = Band.objects.get(
                start_frequency__lte=frequency,
                end_frequency__gte=frequency,
            )
        except Band.DoesNotExist:
            print 'Frequency.DoesNotExist: %f' % frequency
            return {'spot': spot, 'interesting': False}

        filter = Filter.objects.get(operator=operator)
        interesting_bands = filter.bands.all()

        if band.name in [band.name for band in interesting_bands]:
            band_is_interesting = True
        else:
            band_is_interesting = False

        try:
            prefix = Prefix.objects.get(full_callsign=True, name=spot.station)
        except Prefix.DoesNotExist:
            cut = 0
            prefix = None
            while not prefix:
                cut += 1
                if cut == len(spot.station):
                    raise Prefix.DoesNotExist

                prefix_filter = spot.station[:-cut]

                try:
                    prefix = Prefix.objects.get(name=prefix_filter)
                except Prefix.DoesNotExist:
                    continue

        print colors.green(prefix)
        print colors.light_blue(prefix.entity)
        all_entity_prefixes = Prefix.objects.filter(entity=prefix.entity)
        print colors.light_red(all_entity_prefixes)
        print colors.light_red(len(all_entity_prefixes))

        print colors.yellow(filter)

        qsos = QSO.objects.filter(operator=operator).filter(prefix__in=all_entity_prefixes)
        print colors.light_green(qsos)
        print colors.light_green(len(qsos))

        if band_is_interesting and True:
            filtered_spot['interesting'] = True
        else:
            filtered_spot['interesting'] = False

        filtered_spot['spot'] = spot
        return filtered_spot

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

        filter = self.init_filter(operator)
        filter.initialize(operator)

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(self.request, user)
        return super(RegisterView, self).form_valid(form)

    def init_filter(self, operator):
        filter = Filter()
        filter.initialize(operator)
        filter.save()
        for band in Band.objects.all():
            filter.bands.add(band)
        filter.save()

        return filter

class FilterDetailView(DetailView):
    model = Filter
    template_name = "dx/filter_detail.html"

    def get_object(self, queryset=None):
        operator = Operator.objects.get(user__username=self.request.user)
        obj = Filter.objects.get(operator=operator)
        return obj

class FilterEditView(UpdateView):
    model = Filter
    fields = ['bands', 'show_qsl_confirmed', 'show_eqsl_confirmed', 'show_lotw_confirmed']
    success_url = reverse_lazy('filter')

    def get_object(self, queryset=None):
        operator = Operator.objects.get(user__username=self.request.user)
        obj = Filter.objects.get(operator=operator)
        return obj

class ProfileView(DetailView):
    model = User

    def get_object(self, queryset=None):
        obj = User.objects.get(username=self.request.user)
        return obj

class ProfileEdit(UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email']
    success_url = reverse_lazy('profile')
    form_class = ProfileEditForm

    def get_object(self, queryset=None):
        obj = User.objects.get(username=self.request.user)
        return obj

class OperatorView(DetailView):
    model = Operator

    def get_object(self, queryset=None):
        obj = Operator.objects.get(user__username=self.request.user)
        return obj

class OperatorEdit(UpdateView):
    model = Operator
    fields = ['callsign', 'locator']
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
