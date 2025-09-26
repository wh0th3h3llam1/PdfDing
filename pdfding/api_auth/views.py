from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api_auth.models import AccessToken
from api_auth.serializers import (
    ReadOnlyAccessTokenSerializer,
    AccessTokenCreateSerializer,
    AccessTokenRotateSerializer,
)

# Create your views here.


class AccessTokenViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = AccessToken.objects.select_related("knox_token")

    def get_queryset(self):
        return (
            super().get_queryset().filter(user=self.request.user).order_by("-knox_token__created")
        )

    def get_serializer_class(self):
        return (
            AccessTokenCreateSerializer
            if self.action == "create"
            else ReadOnlyAccessTokenSerializer
        )

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        meta = ser.save()
        return Response(
            {
                "token": ser.plaintext_token,  # show once
                "token_key_prefix": meta.token_key_prefix(),
                "id": meta.id,
                "name": meta.name,
                "created": meta.knox_token.created,
                "expiry": meta.knox_token.expiry,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(methods=["POST"], detail=True)
    def rotate(self, request, pk=None):
        meta = self.get_queryset().filter(pk=pk).first()
        if not meta:
            return Response(status=status.HTTP_404_NOT_FOUND)
        ser = AccessTokenRotateSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        new_meta = ser.save(meta=meta)
        return Response(
            {
                "token": ser.plaintext_token,  # show once
                "token_key_prefix": new_meta.token_key_prefix(),
                "id": new_meta.id,
                "name": new_meta.name,
                "created": new_meta.knox_token.created,
                "expiry": new_meta.knox_token.expiry,
            },
            status=status.HTTP_201_CREATED,
        )
