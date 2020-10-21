from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from employee_auth.models import User, Department

APP_TEMPLATE_FOLDER = "dashboard/"


@method_decorator(login_required, name='dispatch')
class IndexView(TemplateView):
    template_name = APP_TEMPLATE_FOLDER + "index.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context["users"] = User.objects.all()
        context["departments"] = Department.objects.all()
        return context
