from django.urls import path

from .views import ShortLinkCreateView, ShortLinkDetailView, expand

urlpatterns = [
    path("links/", ShortLinkCreateView.as_view(), name="create"),
    path("links/<str:short_url>/", ShortLinkDetailView.as_view(),
         name="detail"),
    path("<str:code>/", expand, name="expand"),
]
