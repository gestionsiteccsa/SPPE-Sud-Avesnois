from django.urls import path

from .views.dashboard import (
    DashboardAssistedRequestView,
    DashboardCampaignCloseView,
    DashboardCampaignCreateView,
    DashboardCampaignDetailView,
    DashboardCampaignGoLiveView,
    DashboardCampaignLaunchView,
    DashboardCampaignLettersView,
    DashboardCampaignListView,
    DashboardCampaignRemindView,
    DashboardCampaignTestLaunchView,
    DashboardRequestQueueView,
    DashboardRequestReviewView,
)

app_name = "dashboard_campagnes"

urlpatterns = [
    path("campagnes/", DashboardCampaignListView.as_view(), name="campaign_list"),
    path("campagnes/ajouter/", DashboardCampaignCreateView.as_view(), name="campaign_add"),
    path("campagnes/<int:pk>/", DashboardCampaignDetailView.as_view(), name="campaign_detail"),
    path("campagnes/<int:pk>/lancer/", DashboardCampaignLaunchView.as_view(), name="campaign_launch"),
    path(
        "campagnes/<int:pk>/lancer-test/",
        DashboardCampaignTestLaunchView.as_view(),
        name="campaign_test_launch",
    ),
    path(
        "campagnes/<int:pk>/relancer/",
        DashboardCampaignRemindView.as_view(),
        name="campaign_remind",
    ),
    path(
        "campagnes/<int:pk>/passer-en-reel/",
        DashboardCampaignGoLiveView.as_view(),
        name="campaign_go_live",
    ),
    path(
        "campagnes/<int:pk>/courriers/",
        DashboardCampaignLettersView.as_view(),
        name="campaign_letters",
    ),
    path(
        "campagnes/<int:pk>/cloturer/",
        DashboardCampaignCloseView.as_view(),
        name="campaign_close",
    ),
    path("campagnes/demandes/", DashboardRequestQueueView.as_view(), name="request_queue"),
    path(
        "campagnes/demandes/<int:pk>/traiter/",
        DashboardRequestReviewView.as_view(),
        name="request_review",
    ),
    path(
        "campagnes/demandes/saisir/",
        DashboardAssistedRequestView.as_view(),
        name="assisted_request",
    ),
]