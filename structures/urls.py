from django.urls import path

from . import views

app_name = "structures"

urlpatterns = [
    path("", views.StructureListView.as_view(), name="liste"),
    path("<int:pk>/", views.StructureDetailView.as_view(), name="detail"),
    path("carte/", views.StructureMapView.as_view(), name="carte"),
]
