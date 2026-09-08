from django.urls import path

from . import views

app_name = "feedback"

urlpatterns = [
    path("signaler/", views.FeedbackSubmitView.as_view(), name="submit"),
]
