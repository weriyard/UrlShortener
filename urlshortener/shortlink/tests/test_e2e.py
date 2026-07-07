from unittest.mock import patch

from django.conf import settings
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import ShortLink

CREATE_SHORT_LINK_URL = "/{}/links/".format(settings.SHORT_LINK_PREFIX)
EXAMPLE_LONG_URL = "http://example.com/very-very/long/url/even-longer"


class ShortenAndExpandETest(APITestCase):

    def test_shorten_returns_full_short_url(self) -> None:
        resp = self.client.post(CREATE_SHORT_LINK_URL,
                                {"original_url": EXAMPLE_LONG_URL})

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ShortLink.objects.count(), 1)
        code = ShortLink.objects.get().short_url
        self.assertEqual(len(code), settings.SHORT_URL_CODE_LENGTH)
        self.assertEqual(
            resp.data["short_link"],
            f"http://testserver/{settings.SHORT_LINK_PREFIX}/{code}/",
        )

    def test_shorten_rejects_invalid_url(self) -> None:
        resp = self.client.post(CREATE_SHORT_LINK_URL,
                                {"original_url": "not-a-url"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_expand_redirects_to_original(self) -> None:
        short_link = self.client.post(
            CREATE_SHORT_LINK_URL, {"original_url": EXAMPLE_LONG_URL}).data[
            "short_link"]

        resp = self.client.get(short_link)

        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)
        self.assertEqual(resp.headers["Location"], EXAMPLE_LONG_URL)

    def test_expand_unknown_code_returns_404(self) -> None:
        url = f"/{settings.SHORT_LINK_PREFIX}/nieistnieje/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_returns_original_url_as_json(self) -> None:
        code = self.client.post(
            CREATE_SHORT_LINK_URL, {"original_url": EXAMPLE_LONG_URL}).data[
            "short_link"].rstrip("/").split("/")[-1]

        resp = self.client.get(f"{CREATE_SHORT_LINK_URL}{code}/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["original_url"], EXAMPLE_LONG_URL)


class UniqueCodeGenerationTest(APITestCase):

    def test_retries_on_collision(self) -> None:
        ShortLink.objects.create(original_url="https://x.com/terefere",
                                 short_url="AAAAAAA")
        with patch.object(ShortLink, "generate_short_code",
                          side_effect=["AAAAAAA", "BBBBBBB"]):
            resp = self.client.post(CREATE_SHORT_LINK_URL,
                                    {"original_url": EXAMPLE_LONG_URL})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            resp.data["short_link"],
            f"http://testserver/{settings.SHORT_LINK_PREFIX}/BBBBBBB/",
        )

    def test_stop_after_collisions_limit(self) -> None:
        ShortLink.objects.create(original_url="https://x.com/terefere",
                                 short_url="Xdfe22")
        with patch.object(ShortLink, "generate_short_code",
                          return_value="Xdfe22"):
            resp = self.client.post(CREATE_SHORT_LINK_URL,
                                    {"original_url": EXAMPLE_LONG_URL})
        self.assertEqual(resp.status_code,
                         status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(ShortLink.objects.count(), 1)
