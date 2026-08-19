from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path(
        "protection-des-donnees/",
        views.DataProtectionView.as_view(),
        name="data_protection",
    ),
]
