from django.urls import path
from .views import *
from .job_views import *

urlpatterns = [
    path('addresses/', AddressListView.as_view(), name='addresses'),
    path('addresses/list', AddressListView.as_view(), name='address-list'),
    path('addresses/create', AddressCreateView.as_view(), name='address-create'),
    path('addresses/<int:pk>/', AddressDetailView.as_view(), name='address-detail'),
    path('addresses/<int:pk>/detail', AddressDetailView.as_view(), name='address-detail'),
    path('addresses/<int:pk>/edit', AddressEditView.as_view(), name='address-edit'),
    path('addresses/<int:pk>/delete', AddressDeleteView.as_view(), name='address-delete'),

    path('clients/', ClientListView.as_view(), name='clients'),
    path('clients/list', ClientListView.as_view(), name='client-list'),
    path('clients/create', ClientCreateView.as_view(), name='client-create'),
    path('clients/<int:pk>/', ClientDetailView.as_view(), name='client-detail'),
    path('clients/<int:pk>/detail', ClientDetailView.as_view(), name='client-detail'),
    path('clients/<int:pk>/edit', ClientEditView.as_view(), name='client-edit'),
    path('clients/<int:pk>/delete', ClientDeleteView.as_view(), name='client-delete'),
]

'''
    path('quotes/', QuoteListView.as_view(), name='quotes'),
    path('quotes/list', QuoteListView.as_view(), name='quote-list'),
    path('quotes/create', QuoteCreateView.as_view(), name='quote-create'),
    path('quotes/<int:pk>/', QuoteDetailView.as_view(), name='quote-detail'),
    path('quotes/<int:pk>/detail', QuoteDetailView.as_view(), name='quote-detail'),
    path('quotes/<int:pk>/edit', QuoteEditView.as_view(), name='quote-edit'),
    path('quotes/<int:pk>/delete', QuoteDeleteView.as_view(), name='quote-delete'),
    '''