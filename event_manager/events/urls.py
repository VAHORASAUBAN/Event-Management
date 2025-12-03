from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    EventViewSet,
    EventRSVPCreateView,
    EventRSVPUpdateView,
    EventReviewListCreateView,
)

router = DefaultRouter()
router.register(r"events", EventViewSet, basename="event")

urlpatterns = [
    path("", include(router.urls)),
    path("events/<int:event_id>/rsvp/", EventRSVPCreateView.as_view(), name="event-rsvp"),
    path(
        "events/<int:event_id>/rsvp/<int:user_id>/",
        EventRSVPUpdateView.as_view(),
        name="event-rsvp-update",
    ),
    path(
        "events/<int:event_id>/reviews/",
        EventReviewListCreateView.as_view(),
        name="event-reviews",
    ),
]
