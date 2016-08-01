from .base import all_views
from users.api import all_views as users_views
from .resource import ResourceListViewSet, ResourceViewSet, PurposeViewSet
from .reservation import ReservationViewSet
from .unit import UnitViewSet
from .search import TypeaheadViewSet
from .equipment import EquipmentViewSet

from rest_framework import routers
from rest_framework.decorators import api_view, renderer_classes
from rest_framework import response, schemas
from rest_framework.renderers import CoreJSONRenderer
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer
from rest_framework.reverse import reverse


class RespaAPIRouter(routers.DefaultRouter):
    def __init__(self, schema_title=None, schema_url=None):
        if schema_title or schema_url:
            super(RespaAPIRouter, self).__init__(schema_title=schema_title,
                                                 schema_url=schema_url)
        else:
            super(RespaAPIRouter, self).__init__()
        self.registered_api_views = set()
        self._register_all_views()
        self.register("search", TypeaheadViewSet, base_name="search")

    def _register_view(self, view):
        if view['class'] in self.registered_api_views:
            return
        self.registered_api_views.add(view['class'])
        self.register(view['name'], view['class'], base_name=view.get("base_name"))

    def _register_all_views(self):
        for view in all_views:
            self._register_view(view)
        for view in users_views:
            self._register_view(view)


@api_view()
@renderer_classes([CoreJSONRenderer, OpenAPIRenderer, SwaggerUIRenderer])
def schema_view(request):
    generator = schemas.SchemaGenerator(title='Bookings API',
                                        url=reverse('api-root'))
    return response.Response(generator.get_schema(request=request))
