from __future__ import annotations
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import serializers

from knox.models import AuthToken
from api_auth.models import AccessToken

# Create your serializers here.


def _to_aware(dt):
    # Accept naive datetime; make them aware in current TZ
    if timezone.is_naive(dt):
        return timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


class ReadOnlyAccessTokenSerializer(serializers.ModelSerializer):
    token_id = serializers.IntegerField(source="knox_token.id")
    created = serializers.DateTimeField(source="knox_token.created")
    expiry = serializers.DateTimeField(source="knox_token.expiry")
    prefix = serializers.CharField(source="token_key_prefix")

    class Meta:
        model = AccessToken
        fields = ["id", "token_id", "name", "prefix", "created", "expiry", "last_used"]
        readonly_fields = fields


class AccessTokenCreateSerializer(serializers.ModelSerializer):
    """
    Creates the knox token + metadata. Handles optional expires_at.
    """

    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    _plaintext_token: str = ""  # set after save()

    def validate_expires_at(self, value):
        if value is None:
            return value
        aware = _to_aware(value)
        now = timezone.now()
        if aware <= now + timedelta(seconds=5):
            raise serializers.ValidationError("`expires_at` must be in the future.")
        # (Optional) enforce a max lifetime, e.g. 365 days
        max_expiry = now + timedelta(days=365)
        if aware > max_expiry:
            raise serializers.ValidationError(
                "`expires_at` is too far in the future (max 365 days)."
            )
        return aware

    class Meta:
        model = AccessToken
        fields = ["name", "expires_at"]

    def create(self, validated):
        user = self.context["request"].user
        # 1) create knox token (returns instance + plaintext)

        expires_at = validated.pop("expires_at", None)
        knox_token, token = create_knox_token(user, expires_at)

        # 3) create our metadata
        meta = AccessToken.objects.create(user=user, knox_token=knox_token, **validated)
        # 4) stash plaintext for the view to return once
        self._plaintext_token = token
        return meta


class AccessTokenRotateSerializer(serializers.Serializer):
    """
    Deletes the old token, issues a new one (optionally with expires_at),
    and returns the new plaintext token via self.plaintext_token.
    """

    expires_at = serializers.DateTimeField(required=False, allow_null=True)

    plaintext_token: str | None = None

    def validate_expires_at(self, value):
        if value is None:
            return value
        aware = _to_aware(value)
        if aware <= timezone.now():
            raise serializers.ValidationError("expires_at must be in the future.")
        return aware

    def save(self, *, meta: AccessToken) -> AccessToken:
        user = self.context["request"].user
        if meta.user.id != user.id:  # type: ignore
            raise serializers.ValidationError("Not allowed.")
        name = meta.name
        # remove old (cascades to meta through O2O, so copy name first)
        meta.knox_token.delete()
        # create new
        expires_at = self.validated_data.get("expires_at", None)  # type: ignore
        knox_token, token = create_knox_token(user, expires_at)

        new_meta = AccessToken.objects.create(user=user, knox_token=knox_token, name=name)
        self.plaintext_token = token
        return new_meta


def create_knox_token(user, expires_at) -> tuple[AuthToken, str]:
    return AuthToken.objects.create(user=user, expires_at=expires_at)  # type: ignore
