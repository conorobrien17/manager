from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from employee_auth.models import User, Department
from carbina.models import Quote, Client
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta

APP_TEMPLATE_FOLDER = "dashboard/"


@method_decorator(login_required, name='dispatch')
class IndexView(TemplateView):
    template_name = APP_TEMPLATE_FOLDER + "index.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        # Compute the time delta for a week ago, only logins within the last 7
        # days will be displayed on the list
        one_week_delta = timezone.now() - timezone.timedelta(days=7)
        context["users"] = User.objects.filter(last_login__gte=one_week_delta)[:10]

        context["departments"] = Department.objects.all()

        try:
            context["quotes"] = Quote.objects.latest('-scheduled_time')[:10]
        except ObjectDoesNotExist as e:
            context["quotes"] = ['No upcoming quotes to display!',]

        return context
