from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import View, UpdateView, DetailView, DeleteView, ListView, CreateView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.forms import formset_factory
from django.db import transaction
import django_rq
from .forms import AddressForm, ClientForm, AddressFormSet
from .models import Address, Client
from .apps import APP_TEMPLATE_FOLDER, OK_FLAG, FALSE_FLAG, TRUE_FLAG
from .async_tasks import forward_geocode_call, get_static_map_image, get_navigation_info
from .utils import are_nav_values_loaded

_address_template_path = APP_TEMPLATE_FOLDER + "address/"
_client_template_path = APP_TEMPLATE_FOLDER + "client/"
ADDR_PAGINATE_BY = 15
CLIENT_PAGINATE_BY = 15


# purpose:   provide pagination with proper error handling for any model's
#            list view. The paginated data and number of data in the page
#            is returned.
# inputs:    request     ->  the view request
#            model       ->  the model that will be listed from an all queryset
#   default_paginate_by  ->  integer representing the number of items to be
#                            displayed if the user makes no choice
# returns:   - the paginated data and the count of items paginated
def select_paginate(request, queryset, default_paginate_by):
    paginate_by = request.GET.get('paginate_by', )

    if not paginate_by and default_paginate_by:
        paginate_by = default_paginate_by

    paginator = Paginator(queryset, paginate_by)
    page = request.GET.get('page', )

    try:
        paginated = paginator.get_page(page)
    except PageNotAnInteger:
        paginated = paginator.get_page(1)
    except EmptyPage:
        paginated = paginator.page(paginator.num_pages)

    return {'DataPaginated': paginated, 'paginate_by': paginate_by}


# purpose:   provide an authenticated user with a form to create an Address
#            object. The object's created_by field is set to the user after
#            the form is validated.
# returns:   - detail page of the created address if the form is valid
#            - if the form has errors, the page will be rendered again with errors
@method_decorator(login_required, name="dispatch")
class AddressCreateView(View):
    model = Address
    form_class = AddressForm
    template_name = _address_template_path + "create.html"
    redis_conn = django_rq.get_connection('default')

    def get(self, request, *args, **kwargs):
        context = {"form": self.form_class}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            address_object = form.save(commit=False)
            address_object.created_by = request.user
            address_object.save()
            self.redis_conn.enqueue(forward_geocode_call, address_object)
            return HttpResponseRedirect(reverse_lazy("address-detail", args=[address_object.pk]))
        return render(request, self.template_name, {"form": form})


@method_decorator(login_required, name="dispatch")
class AddressEditView(UpdateView):
    model = Address
    form_class = AddressForm
    template_name = _address_template_path + "edit.html"


@method_decorator(login_required, name="dispatch")
class AddressListView(ListView):
    model = Address
    template_name = _address_template_path + "list.html"
    context_object_name = "addresses"
    paginate_by = ADDR_PAGINATE_BY


@method_decorator(login_required, name="dispatch")
class AddressDetailView(DetailView):
    model = Address
    template_name = _address_template_path + 'detail.html'
    context_object_name = 'address'
    redis_conn = django_rq.get_connection('default')

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

    def get_object(self, queryset=model):
        return get_object_or_404(self.model, pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super(AddressDetailView, self).get_context_data(**kwargs)
        if not self.object.static_map:
            self.redis_conn.enqueue(get_static_map_image, self.object)
        _address_str = str(self.object.street + ",+" + self.object.city + "+" + self.object.state).replace(' ', '+')
        context['address_map_url'] = _address_str
        context['street_label'] = str(self.object.street).replace(" ", "+")
        return context


@method_decorator(login_required, name="dispatch")
class AddressDeleteView(DeleteView):
    model = Address
    template_name = _address_template_path + "delete.html"
    success_url = reverse_lazy("address-list")


@method_decorator(login_required, name="dispatch")
class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    template_name = _client_template_path + "create.html"
    redis_conn = django_rq.get_connection('default')
    queue = django_rq.get_queue("default")

    def get_context_data(self, **kwargs):
        context = super(ClientCreateView, self).get_context_data(**kwargs)
        if self.request.POST and self.request.form:
            context['addresses'] = AddressFormSet(self.request.POST)
        else:
            context['addresses'] = AddressFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        addresses = context['addresses']
        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.created_by = self.request.user
            self.object = form.save()
            if addresses.is_valid():
                for address in addresses:
                    new_addr = address.save(commit=False)
                    new_addr.client = self.object
                    address.save()
                    self.queue.enqueue(forward_geocode_call, address)
        return super(ClientCreateView, self).form_valid(form)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        address_formset = AddressFormSet(request.POST or None, instance=form.instance)
        if form.is_valid() and address_formset.is_valid():
            client_object = form.save(commit=False)
            client_object.created_by = request.user
            client_object.save()
            # Iterate through the submitted addresses in the formset
            for address in address_formset:
                # Create the address object and set the client as the property owner
                new_addr = address.save(commit=False)
                new_addr.client = client_object
                new_addr.save()
                # After saving the address, enqueue an API call to get the coordinates of the address
                # The worker that gets called will update the DB with the latitude and longitude
                # asynchronously
                self.queue.enqueue(forward_geocode_call, new_addr)
            return HttpResponseRedirect(reverse_lazy("client-detail", args=[client_object.pk]))
        return render(request, self.template_name, {"form": form})


@method_decorator(login_required, name="dispatch")
class ClientEditView(UpdateView):
    model = Client
    form_class = AddressForm
    template_name = _client_template_path + "edit.html"


@method_decorator(login_required, name="dispatch")
class ClientListView(ListView):
    model = Client
    template_name = _client_template_path + "list.html"
    context_object_name = 'clients'
    paginate_by = CLIENT_PAGINATE_BY


@method_decorator(login_required, name="dispatch")
class ClientDetailView(DetailView):
    model = Client
    template_name = _client_template_path + 'detail.html'
    context_object_name = 'client'
    queue = django_rq.get_queue('default')

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

    def get_object(self, queryset=model):
        return get_object_or_404(self.model, pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super(ClientDetailView, self).get_context_data(**kwargs)
        for address in self.object.addresses.all():
            if not address.static_map:
                self.queue.enqueue(get_static_map_image, address)
            if are_nav_values_loaded(address) != TRUE_FLAG:
                self.queue.enqueue(get_navigation_info, address)
        return context


@method_decorator(login_required, name="dispatch")
class ClientDeleteView(DeleteView):
    model = Client
    template_name = _client_template_path + "delete.html"
    success_url = reverse_lazy("client-list")
