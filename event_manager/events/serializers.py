from django.contrib.auth.models import User
from rest_framework import serializers

from .models import UserProfile, Event, RSVP, Review


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "username",
            "email",
            "full_name",
            "bio",
            "location",
            "profile_picture",
        ]


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "profile"]


class EventSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    invited_users = serializers.PrimaryKeyRelatedField(
        many=True, read_only=False, queryset=User.objects.all(), required=False
    )

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "organizer",
            "location",
            "start_time",
            "end_time",
            "is_public",
            "invited_users",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["organizer", "created_at", "updated_at"]

    def validate(self, attrs):
        start = attrs.get("start_time") or getattr(self.instance, "start_time", None)
        end = attrs.get("end_time") or getattr(self.instance, "end_time", None)
        if start and end and end <= start:
            raise serializers.ValidationError(
                {"end_time": "end_time must be after start_time."}
            )
        return attrs

    def create(self, validated_data):
        invited_users = validated_data.pop("invited_users", [])
        event = Event.objects.create(**validated_data)   # organizer removed
        if invited_users:
            event.invited_users.set(invited_users)
        return event

    def update(self, instance, validated_data):
        invited_users = validated_data.pop("invited_users", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if invited_users is not None:
            instance.invited_users.set(invited_users)
        return instance


class RSVPSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = RSVP
        fields = ["id", "event", "user", "status", "created_at", "updated_at"]
        read_only_fields = ["event", "user", "created_at", "updated_at"]


class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ["id", "event", "user", "rating", "comment", "created_at"]
        read_only_fields = ["event", "user", "created_at"]

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
