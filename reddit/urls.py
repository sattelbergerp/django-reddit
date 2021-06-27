from django.urls import path, include
from .views import PostViewSet
from rest_framework import routers

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'posts', PostViewSet, basename='Post')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
app_name = 'reddit'
urlpatterns = [
    path('', include(router.urls)),
]