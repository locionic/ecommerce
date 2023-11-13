from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework import viewsets, generics

from users.api.v1.serializers import UserSerializer, UserPostPutPatchSerializer
from store.api.v1.permissions import SelfOrReadOnly
from rest_framework.permissions import IsAdminUser

User = get_user_model()

class UserDetail(generics.RetrieveUpdateAPIView):
    lookup_field = "username"
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser | SelfOrReadOnly]

    @method_decorator(cache_page(300))
    def get(self, *args, **kwargs):
        return super(UserDetail, self).get(*args, *kwargs)

    def get_serializer_class(self):
        if (self.request.method == 'GET'):
            return self.serializer_class
        return UserPostPutPatchSerializer