# SPDX-FileCopyrightText: 2025-present Tobias Kunze
# SPDX-License-Identifier: AGPL-3.0-only WITH LicenseRef-Pretalx-AGPL-3.0-Terms

from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from pretalx import __version__
from pretalx.api.versions import CURRENT_VERSION


class MetadataView(APIView):
    """
    Returns metadata about the API, including version information and links to key endpoints.
    """

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="API Metadata",
        description="Returns metadata about the API, including version information and links to key endpoints.",
        tags=["metadata"],
    )
    def get(self, request, format=None):
        return Response(
            {
                "api_version": CURRENT_VERSION,
                "pretalx_version": __version__,
                "events": request.build_absolute_uri("/api/events/"),
            }
        )
