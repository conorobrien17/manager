from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.generic import View, UpdateView, DetailView, DeleteView, ListView, CreateView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .forms import QuoteForm, QuoteFormSet
from .models import Quote, QuoteItem, Job, JobPicture
from .apps import APP_TEMPLATE_FOLDER, OK_FLAG, FALSE_FLAG, TRUE_FLAG

_quote_template_path = APP_TEMPLATE_FOLDER + "quotes/"


@method_decorator(login_required, name="dispatch")
class QuoteCreateView(CreateView):
    model = Quote
    form_class = QuoteForm
    template_name = _quote_template_path + 'create.html'

    def get_context_data(self, **kwargs):
        context = super(QuoteCreateView, self).get_context_data(**kwargs)
        if self.request.POST and self.request.form:
            context['quote_items'] = QuoteFormSet(self.request.POST, prefix='quote_item')
        else:
            context['quote_items'] = QuoteFormSet(prefix='quote_item')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        quote_items = context['quote_items']
        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.author = self.request.user
            self.object = form.save()

            if quote_items.is_valid():
                for item in quote_items:
                    item.save(commit=False)
                    item.author = self.request.user
                    item.quote = self.object
                    item.save(commit=True)
        return super(QuoteCreateView, self).form_valid(form)

    def post(self, *args, **kwargs):
        form = self.form_class(self.request.POST)
