from django.contrib import admin
from .models import UserProfile, Event, RSVP, Review


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "full_name", "location")
    search_fields = ("full_name", "user__username")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "organizer", "location", "start_time", "is_public")
    search_fields = ("title", "organizer__username", "location")
    list_filter = ("is_public", "location")
    filter_horizontal = ("invited_users",)


@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "user", "status", "created_at")
    list_filter = ("status",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "user", "rating", "created_at")
    search_fields = ("event__title", "user__username")
