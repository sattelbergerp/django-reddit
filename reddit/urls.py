from django.urls import path, include
from .models import User, Post
from rest_framework import routers, serializers, viewsets

# Serializers define the API representation.
class PostSerializer(serializers.Serializer):
    title = serializers.CharField()
    text = serializers.CharField(required=False)
    link = serializers.CharField(required=False)
    score = serializers.IntegerField()
    votes = serializers.IntegerField()

# ViewSets define the view behavior.
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'posts', PostViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
app_name = 'reddit'
urlpatterns = [
    path('', include(router.urls)),
]