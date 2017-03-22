from tastypie.api import Api

from .api import TagResource, TopicCategoryResource, ProfileResource, \
    GroupResource, RegionResource, OwnersResource
from .resourcebase_api import LayerResource, MapResource, DocumentResource, \
    ResourceBaseResource, FeaturedResourceBaseResource
from django.conf.urls import patterns, url

api = Api(api_name='api')

urlpatterns = patterns(
    'geonode.api.views',
    url(r'^total_count', 'total_count', name="total_count"),
)

api.register(LayerResource())
api.register(MapResource())
api.register(DocumentResource())
api.register(ProfileResource())
api.register(ResourceBaseResource())
api.register(TagResource())
api.register(RegionResource())
api.register(TopicCategoryResource())
api.register(GroupResource())
api.register(FeaturedResourceBaseResource())
api.register(OwnersResource())
