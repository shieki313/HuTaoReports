from django.urls import path

from .views import IndexView, AboutView, ProcessImageView

urlpatterns = [
    path('', IndexView.as_view(), name="index"),
    path('aboutus/', AboutView.as_view(), name="about"),
    path('process_image/', ProcessImageView.as_view(), name="process_image")
]
