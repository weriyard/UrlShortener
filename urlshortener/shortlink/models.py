import secrets

from django.conf import settings
from django.db import models


class ShortLink(models.Model):
    original_url = models.URLField()
    short_url = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_short_code(
            length: int = settings.SHORT_URL_CODE_LENGTH) -> str:
        """Return a random code of a fixed length."""
        return "".join(secrets.choice(settings.ALPHABET) for _ in range(length))

    def __str__(self) -> str:
        return f"{self.short_url} -> {self.original_url}"
