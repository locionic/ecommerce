from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers, vary_on_cookie
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework import viewsets, generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from store.api.v1.permissions import CreatorModifyOrReadOnly, IsAdminUserForObject, \
    IsSellerUser, SellerModifyOrReadOnly, IsReviewReadOnly, CategoryPermission, \
    CreateOrCreatorModify
from store.api.v1.serializers import ProductSerializer, ProductDetailSerializer,\
    AlbumSerializer, ReviewSerializer, CategorySerializer
from store.models import Product, Album, Category, Review
from users.api.v1.serializers import UserSerializer


User = get_user_model()


@method_decorator(cache_page(300))
@method_decorator(vary_on_headers("Authorization"))
@method_decorator(vary_on_cookie)
@action(methods=["get"], detail=False, name="data owned by logged in user")
def mine(self, request):
    if request.user.is_anonymous:
        raise PermissionDenied("You must be logged in to see which Images are yours")
    data = self.get_queryset().filter(created_by=request.user)

    page = self.paginate_queryset(data)
    if page is not None:
        serializer = self.get_serializer_class()(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)
    serializer = self.get_serializer_class()(data, many=True, context={"request": request})
    return Response(serializer.data)


viewsets.ModelViewSet.mine = mine


class ProductViewSet(viewsets.ModelViewSet):
    lookup_field = "slug"
    queryset = Product.objects.all()
    permission_classes = [IsReviewReadOnly | SellerModifyOrReadOnly | IsAdminUserForObject | IsSellerUser]

    def get_serializer_class(self):
        if self.action in ('list', 'create'):
            return ProductSerializer
        return ProductDetailSerializer

    def get_queryset(self):
        search = self.request.query_params.get('search')
        if search:
            return Product.objects.filter(Q(title__icontains=search) | Q(description__icontains=search))
        return self.queryset


class CategoryViewSet(viewsets.ModelViewSet):
    lookup_field = "slug"
    queryset = Category.objects.all()
    permission_classes = [CategoryPermission]
    serializer_class = CategorySerializer

    def retrieve(self, request, *args, **kwargs):
        """
        Returns the products in category -> Category details
        """
        category = get_object_or_404(Category, slug=kwargs.get('slug'))

        query_set = Product.objects.filter(category=category)

        # create a custom pagination for the products
        paginator = PageNumberPagination()
        paginator.page_size = settings.PAGINATION_PAGE_SIZE
        query_set = paginator.paginate_queryset(query_set, request)
        paginator.page_query_param = 'page'

        # category information for json response
        category = CategorySerializer(category).data
        # products list for json response
        products = ProductSerializer(query_set, many=True, context={'request': request}).data
        return Response(
            {
                "category": category,
                "products": {
                    "count": paginator.page.paginator.count,
                    "next": paginator.get_next_link(),
                    "previous": paginator.get_previous_link(),
                    "results": products
                }
            }
        )


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    permission_classes = [CreateOrCreatorModify]
    serializer_class = ReviewSerializer
    content_type_pk = ContentType.objects.get(app_label="store", model="product").pk

    def create(self, request, *args, **kwargs):
        custom_data = request.data
        print(request.user)
        custom_data['content_type'] = self.content_type_pk
        print(custom_data)
        serializer = self.get_serializer(data=custom_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        if not self.request.user.is_anonymous:
            serializer.save(created_by=self.request.user)


class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    permission_classes = [CreatorModifyOrReadOnly | IsAdminUserForObject]
    serializer_class = AlbumSerializer

