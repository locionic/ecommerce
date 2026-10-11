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

# An unbounded term turns every request into a full-table `%term%` scan: `?search=%20`
# used to match every row that happens to contain a space, and a multi-kilobyte term
# is no cheaper. Terms are normalized and capped before they reach the database.
MAX_SEARCH_LENGTH = 100


def normalized_search_term(request):
    """
    Return the trimmed search term for a request, or '' when there isn't a usable one.
    Collapsing internal whitespace keeps the LIKE pattern bounded and predictable.
    """
    term = request.query_params.get('search', '')
    if not isinstance(term, str):
        return ''
    return ' '.join(term.split())[:MAX_SEARCH_LENGTH]


def filter_products(queryset, request):
    """
    Apply the catalog filters shared by the product list and the category detail
    endpoints: an optional search term and an optional list of category slugs.
    """
    term = normalized_search_term(request)
    if term:
        queryset = queryset.filter(
            Q(title__icontains=term) | Q(description__icontains=term)
        )

    slugs = [slug for slug in request.query_params.getlist('category') if slug]
    if slugs:
        # Semi-join on the category slugs instead of joining the categories table, and
        # an unknown slug resolves to an empty result set rather than a 404.
        queryset = queryset.filter(
            category_id__in=Category.objects.filter(slug__in=slugs).values('pk')
        )

    return queryset


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
    # `category` is serialized on every row and `created_by` is a hyperlinked field
    # that reverse()s a URL, so both are pulled in to keep list pages at one query.
    queryset = Product.objects.select_related('category', 'created_by')
    permission_classes = [IsReviewReadOnly | SellerModifyOrReadOnly | IsAdminUserForObject | IsSellerUser]

    def get_serializer_class(self):
        if self.action in ('list', 'create'):
            return ProductSerializer
        return ProductDetailSerializer

    def get_queryset(self):
        return filter_products(super().get_queryset(), self.request)


class CategoryViewSet(viewsets.ModelViewSet):
    lookup_field = "slug"
    queryset = Category.objects.select_related('created_by').all()
    permission_classes = [CategoryPermission]
    serializer_class = CategorySerializer

    def retrieve(self, request, *args, **kwargs):
        """
        Returns the products in category -> Category details
        """
        category = get_object_or_404(Category, slug=kwargs.get('slug'))

        query_set = Product.objects.filter(category=category).select_related('category', 'created_by')
        query_set = filter_products(query_set, request)

        paginator = PageNumberPagination()
        paginator.page_query_param = 'page'
        paginator.page_size = settings.PAGINATION_PAGE_SIZE
        page = paginator.paginate_queryset(query_set, request)

        # category information for json response
        category = CategorySerializer(category).data
        # products list for json response
        products = ProductSerializer(page, many=True, context={'request': request}).data
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
        custom_data['content_type'] = self.content_type_pk
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

