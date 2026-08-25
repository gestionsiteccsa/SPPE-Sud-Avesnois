from django.urls import path

from .views.public import VerificationView

app_name = "campagnes"

urlpatterns = [
    path("verification/<str:token>/", VerificationView.as_view(), name="verification"),
]