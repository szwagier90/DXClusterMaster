from django.shortcuts import render
from django.template.loader import render_to_string

from django.http import HttpResponse, JsonResponse
from django.core.urlresolvers import reverse, reverse_lazy

from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView
from django.views.generic import View

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from models import Spot, Operator, Entity, Band, Prefix, QSO, FileProcessingProgress, Filter
from forms import LogUploadForm, ProfileEditForm, OperatorEditForm, FilterEditForm

from tempfile import NamedTemporaryFile

import sys
import subprocess
import time

from drafts import colors

def filter_spot(spot, operator):
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
                return None

            prefix_filter = spot.station[:-cut]

            try:
                prefix = Prefix.objects.get(name=prefix_filter)
            except Prefix.DoesNotExist:
                continue

    filtered_spot['entity_name'] = prefix.entity.name
    all_entity_prefixes = Prefix.objects.filter(entity=prefix.entity)

    qsos = QSO.objects.filter(operator=operator).filter(prefix__in=all_entity_prefixes)

    not_confirmed = []
    if filter.show_qsl_confirmed:
        qsl_confirmed_qsos = qsos.filter(qsl_confirmed=True)
        if qsl_confirmed_qsos:
            not_confirmed.append(False)
        else:
            not_confirmed.append(True)
    else:
        not_confirmed.append(False)

    if filter.show_eqsl_confirmed:
        eqsl_confirmed_qsos = qsos.filter(eqsl_confirmed=True)
        if eqsl_confirmed_qsos:
            not_confirmed.append(False)
        else:
            not_confirmed.append(True)
    else:
        not_confirmed.append(False)

    if filter.show_lotw_confirmed:
        lotw_confirmed_qsos = qsos.filter(lotw_confirmed=True)
        if lotw_confirmed_qsos:
            not_confirmed.append(False)
        else:
            not_confirmed.append(True)
    else:
        not_confirmed.append(False)

    if True in not_confirmed:
        spot_is_interesting = True
    else:
        spot_is_interesting = False

    if band_is_interesting and spot_is_interesting:
        filtered_spot['interesting'] = True
    else:
        filtered_spot['interesting'] = False

    filtered_spot['spot'] = spot

    return filtered_spot

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
            spots = [filter_spot(spot, operator) for spot in ten_recent_spots]

        context['ten_recent_spots'] = spots
        context['last_id'] = ten_recent_spots[0].id

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
    form_class = FilterEditForm

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
    form_class = OperatorEditForm

    def get_object(self, queryset=None):
        obj = Operator.objects.get(user__username=self.request.user)
        return obj

class LogUploadView(FormView):
    template_name = 'dx/upload.html'
    form_class = LogUploadForm
    success_url = reverse_lazy('upload')

    def get_context_data(self, **kwargs):
        context = super(LogUploadView, self).get_context_data(**kwargs)

        operator = Operator.objects.get(user__username=self.request.user)
        try:
            fpp = FileProcessingProgress.objects.get(operator=operator)
        except FileProcessingProgress.DoesNotExist:
            pass
        except FileProcessingProgress.MultipleObjectsReturned:
            pass
        else:
            progress = 100*fpp.progress/fpp.goal
            context = {'processing': True, 'width': progress}

        return context

    def form_valid(self, form, **kwargs):
        self.handle_uploaded_file(self.request.FILES['file'])
        return render(self.request, self.template_name, {'processing': True})

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

def progress(request):
    operator = Operator.objects.get(user__username=request.user)
    try:
        fpp = FileProcessingProgress.objects.get(operator=operator)
    except FileProcessingProgress.DoesNotExist:
        return JsonResponse({'finished': True})
    except FileProcessingProgress.MultipleObjectsReturned:
        fpp = FileProcessingProgress.filter.get(operator=operator).order_by('-id')[0]
        FileProcessingProgress.filter.get(operator=operator).order_by('-id')[1:].delete()
    progress = 100*fpp.progress/fpp.goal
    return JsonResponse({'finished': False, 'width': progress})

def new_spot(request):
    template_name = 'dx/spot.html'

    id = int(request.POST.get('id', ''))
    id += 1

    sleep_time = 5

    while(True):
        try:
            time.sleep(sleep_time)
            last_spot = Spot.objects.get(id=id)
            break
        except Spot.DoesNotExist:
            sleep_time += 1

    try:
        operator = Operator.objects.get(user__username=request.user)
        spot = filter_spot(last_spot, operator)
        spot_html = render_to_string(template_name, {'spot': spot['spot']})
        return JsonResponse({'id': id, 'interesting': spot['interesting'], 'spot': spot_html})
    except Operator.DoesNotExist:
        spot_html = render_to_string(template_name, {'spot': last_spot})
        return JsonResponse({'id': id, 'interesting': False, 'spot': spot_html})

