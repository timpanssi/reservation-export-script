from django.conf.urls import url
from rest_framework import routers
from respa_payments.api import OrderPostView, OrderCallbackView

urlpatterns = [
    url(r'^order-post/', OrderPostView.as_view()),
    url(r'^order-callback/', OrderCallbackView.as_view()),
]
