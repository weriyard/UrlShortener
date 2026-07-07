from typing import Any

from django.db import IntegrityError, transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from rest_framework import generics
from rest_framework.exceptions import APIException
from rest_framework.serializers import BaseSerializer

from .models import ShortLink
from .serializers import ShortLinkReadSerializer, ShortLinkSerializer


def expand(request: HttpRequest, code: str) -> HttpResponse:
    """Opening a short link and redirects (302) to the original URL."""
    link = get_object_or_404(ShortLink, short_url=code)
    return redirect(link.original_url)


class ShortLinkCreateView(generics.CreateAPIView[ShortLink]):
    """Takes original url and returns the generated short link."""

    queryset = ShortLink.objects.all()
    serializer_class = ShortLinkSerializer

    def perform_create(self, serializer: BaseSerializer[Any]) -> None:
        for _ in range(5):
            try:
                # savepoint for each try - when an IntegrityError occur
                # transaction is broken, without a rollback the next
                # save() would fail
                with transaction.atomic():
                    serializer.save(
                        short_url=ShortLink.generate_short_code())
                return
            except IntegrityError:
                continue
        raise APIException("Could not generate a unique code.")


class ShortLinkDetailView(generics.RetrieveAPIView[ShortLink]):
    """Return the original long url for a given code."""

    queryset = ShortLink.objects.all()
    serializer_class = ShortLinkReadSerializer
    lookup_field = "short_url"
