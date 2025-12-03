from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db import models 
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Event, RSVP, Review
from .serializers import EventSerializer, RSVPSerializer, ReviewSerializer
from .permissions import IsOrganizerOrReadOnly, IsInvitedOrPublic

class EventViewSet(viewsets.ModelViewSet):
    """
    - POST /events/
    - GET /events/
    - GET /events/{id}/
    - PUT/PATCH /events/{id}/
    - DELETE /events/{id}/
    """

    serializer_class = EventSerializer
    queryset = Event.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOrganizerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["location", "is_public", "organizer"]
    search_fields = ["title", "location", "description", "organizer__username"]
    ordering_fields = ["start_time", "created_at"]

    def get_queryset(self):
        user = self.request.user
        # Only public events OR events user organizes OR is invited to
        base_qs = Event.objects.all()
        if user.is_authenticated:
            return base_qs.filter(
                models.Q(is_public=True)
                | models.Q(organizer=user)
                | models.Q(invited_users=user)
            ).distinct()
        return base_qs.filter(is_public=True)

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)


class EventRSVPCreateView(generics.CreateAPIView):
    """
    POST /events/{event_id}/rsvp/
    """

    serializer_class = RSVPSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_event(self):
        event_id = self.kwargs["event_id"]
        return get_object_or_404(Event, pk=event_id)

    def perform_create(self, serializer):
        event = self.get_event()
        user = self.request.user
        # prevent duplicate RSVP
        if RSVP.objects.filter(event=event, user=user).exists():
            raise PermissionDenied("You have already RSVPed for this event.")
        serializer.save(event=event, user=user)


class EventRSVPUpdateView(generics.UpdateAPIView):
    """
    PATCH /events/{event_id}/rsvp/{user_id}/
    (Usually user updates their own RSVP; organizer could also be allowed if needed.)
    """

    serializer_class = RSVPSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["patch"]

    def get_object(self):
        event = get_object_or_404(Event, pk=self.kwargs["event_id"])
        user = get_object_or_404(User, pk=self.kwargs["user_id"])
        rsvp = get_object_or_404(RSVP, event=event, user=user)

        # Only the RSVP owner can update their status
        if self.request.user != user:
            raise PermissionDenied("You can only update your own RSVP.")
        return rsvp


class EventReviewListCreateView(generics.ListCreateAPIView):
    """
    GET /events/{event_id}/reviews/
    POST /events/{event_id}/reviews/
    """

    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_event(self):
        event_id = self.kwargs["event_id"]
        event = get_object_or_404(Event, pk=event_id)
        # Permission: private event reviews only accessible if invited or organizer
        perm = IsInvitedOrPublic()
        if not perm.has_object_permission(self.request, self, event):
            raise PermissionDenied("You are not allowed to access this event.")
        return event

    def get_queryset(self):
        event = self.get_event()
        return Review.objects.filter(event=event)

    def perform_create(self, serializer):
        event = self.get_event()
        user = self.request.user
        if Review.objects.filter(event=event, user=user).exists():
            raise PermissionDenied("You have already reviewed this event.")
        serializer.save(event=event, user=user)
