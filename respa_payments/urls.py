from django.conf.urls import url
from rest_framework import routers
from respa_payments.api import OrderView, CompleteOrderView

urlpatterns = [
    url(r'^order/', OrderView.as_view()),
    url(r'^order-complete/', CompleteOrderView.as_view()),
]
