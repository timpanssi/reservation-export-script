from .base import register_view

from django_orghierarchy.api import OrganizationViewSet

register_view(OrganizationViewSet, 'organization')
