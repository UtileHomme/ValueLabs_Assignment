from django.urls import path
from .views import UniqueTrackingNumber

urlpatterns = [
    path('next-tracking-number/', UniqueTrackingNumber.as_view(), name='next-tracking-number'),
]
