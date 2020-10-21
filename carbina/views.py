from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import View, UpdateView, DetailView, DeleteView, ListView
from .forms import AddressForm
from .models import Address
from .apps import APP_TEMPLATE_FOLDER

_address_template_path = APP_TEMPLATE_FOLDER + "address/"


# purpose:   provide an authenticated user with a form to create an Address
#            object. The object's created_by field is set to the user after
#            the form is validated.
@method_decorator(login_required, name="dispatch")
class AddressCreateView(View):
    model = Address
    form_class = AddressForm
    template_name = _address_template_path + "create.html"

    def get(self, request, *args, **kwargs):
        context = {"form": self.form_class}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            address_object = form.save(commit=False)
            address_object.created_by = request.user
            address_object.save()
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
    # paginate by


@method_decorator(login_required, name="dispatch")
class AddressDetailView(DetailView):
    model = Address
    template_name = _address_template_path + "detail.html"


@method_decorator(login_required, name="dispatch")
class AddressDeleteView(DeleteView):
    model = Address
    template_name = _address_template_path + "delete.html"
    success_url = reverse_lazy("address-list")