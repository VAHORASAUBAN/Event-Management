from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from events.models import Event
class EventAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_create_event(self):
        url = reverse("event-list")
        data = {
            "title": "Demo Event",
            "description": "Just testing",
            "location": "Online",
            "start_time": "2030-01-01T10:00:00Z",
            "end_time": "2030-01-01T12:00:00Z",
            "is_public": True,
        }
        resp = self.client.post(url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.first().organizer, self.user)

    def test_list_public_events(self):
        Event.objects.create(
            title="Public",
            description="Public event",
            location="City",
            start_time="2030-01-01T10:00:00Z",
            end_time="2030-01-01T12:00:00Z",
            organizer=self.user,
            is_public=True,
        )
        url = reverse("event-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 1)
