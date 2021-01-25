from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.generic import View, UpdateView, DetailView, DeleteView, ListView, CreateView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .forms import QuoteForm, QuoteItemFormSet, _quote_item_formset_prefix
from .models import Quote, QuoteItem, HistoryLogUpdate, HistoryLog, QuoteHistoryLog, Job, JobPicture
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
            context['quote_items'] = QuoteItemFormSet(self.request.POST, prefix=_quote_item_formset_prefix)
        else:
            context['quote_items'] = QuoteItemFormSet(prefix=_quote_item_formset_prefix)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        quote_items = context['quote_items']
        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.author = self.request.user
            self.object = form.save()

            if quote_items.is_valid():
                for quote_item in quote_items:
                    quote_item.save(commit=False)
                    quote_item.author = self.request.user
                    quote_item.quote = self.object
                    quote_item.save(commit=True)
        return super(QuoteCreateView, self).form_valid(form)

    def post(self, *args, **kwargs):
        form = self.form_class(self.request.POST)
        item_formset = QuoteItemFormSet(self.request.POST or None, instance=form.instance,
                                        prefix=_quote_item_formset_prefix)

        if form.is_valid() and item_formset.is_valid():
            quote_object = form.save(commit=False)
            quote_object.created_by = self.request.user
            quote_object.save()

            history_log = QuoteHistoryLog.objects.create(quote=self.object).save(commit=True)
            history_log_update = HistoryLogUpdate.objects.create(
                title='Quote Created',
                theme='success',
                history_log=history_log,
                author=self.request.user
            ).save(commit=True)

            for quote_item in item_formset:
                new_q_item = quote_item.save(commit=False)
                new_q_item.author = self.request.user
                new_q_item.save()

            return HttpResponseRedirect(reverse_lazy('quote-detail', args=[quote_object.pk]))
        return render(self.request, self.template_name, {'form': form, 'quote_items': item_formset})


@method_decorator(login_required, name="dispatch")
class QuoteDetailView(DetailView):
    model = Quote
    template_name = _quote_template_path + 'detail.html'
    context_object_name = 'quote'


@method_decorator(login_required, name="dispatch")
class QuoteListView(ListView):
    model = Quote
    template_name = _quote_template_path + 'list.html'
    context_object_name = 'quotes'
