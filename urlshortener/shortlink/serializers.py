from django.conf import settings
from django.http import HttpRequest
from rest_framework import serializers

from .models import ShortLink


class ShortLinkSerializer(serializers.ModelSerializer[ShortLink]):
    """Takes the original url and returns a short link."""

    short_link = serializers.SerializerMethodField()

    class Meta:
        model = ShortLink
        fields = ["original_url", "short_link"]
        extra_kwargs = {"original_url": {"write_only": True}}

    def get_short_link(self, link: ShortLink) -> str:
        path = f"/{settings.SHORT_LINK_PREFIX}/{link.short_url}/"
        request: HttpRequest = self.context["request"]
        return request.build_absolute_uri(path)


class ShortLinkReadSerializer(serializers.ModelSerializer[ShortLink]):
    """Returns the original url for a given code."""

    class Meta:
        model = ShortLink
        fields = ["original_url"]
