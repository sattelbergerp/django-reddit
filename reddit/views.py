from django.http.response import HttpResponse
from django.shortcuts import render
from django_registration.backends.one_step.views import RegistrationView as BaseRegistrationView
from rest_framework import viewsets
from .models import Post
from .serializers import PostSerializer, PostDetailSerializer

# Create your views here.

class RegistrationView(BaseRegistrationView):
    success_url = '/'

class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostDetailSerializer

    def get_serializer_class(self, *args, **kwargs):
        print(self.action)
        if self.action == 'retrieve':
            return PostDetailSerializer
        else:
            return PostSerializer
    
    def get_queryset(self):
        return Post.objects.sort(type=self.request.GET.get('sort', 'hot'))