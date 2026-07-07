from unittest.mock import patch

from django.conf import settings
from django.db import IntegrityError
from django.test import TestCase

from ..models import ShortLink


class GenerateShortCodeTest(TestCase):

    def test_default_length(self) -> None:
        self.assertEqual(len(ShortLink.generate_short_code()),
                         settings.SHORT_URL_CODE_LENGTH)

    def test_explicit_length(self) -> None:
        self.assertEqual(len(ShortLink.generate_short_code(8)), 8)

    def test_only_alphabet_chars(self) -> None:
        code = ShortLink.generate_short_code(50)
        self.assertTrue(all(c in settings.ALPHABET for c in code))

    def test_returns_str(self) -> None:
        self.assertIsInstance(ShortLink.generate_short_code(), str)

    def test_empty_alphabet_raises(self) -> None:
        with patch.object(settings, "ALPHABET", ""):
            with self.assertRaises(IndexError):
                ShortLink.generate_short_code(5)


class ShortLinkModelTest(TestCase):

    def test_short_url_must_be_unique(self) -> None:
        ShortLink.objects.create(original_url="https://a.com",
                                 short_url="abc123")
        with self.assertRaises(IntegrityError):
            ShortLink.objects.create(original_url="https://b.com",
                                     short_url="abc123")

    def test_save_valid_object(self) -> None:
        link = ShortLink.objects.create(
            original_url="https://example.com",
            short_url=ShortLink.generate_short_code(),
        )
        self.assertIsNotNone(link.pk)
        self.assertIsNotNone(link.created_at)

    def test_generated_code_fits_in_column(self) -> None:
        max_length = ShortLink._meta.get_field("short_url").max_length
        self.assertTrue(max_length is not None and
                        settings.SHORT_URL_CODE_LENGTH <= max_length)
