from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers, vary_on_cookie
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models import Q, Prefetch, Min, Max, Count

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


def compute_facets(queryset):
    """
    Computes faceted aggregation metrics for a product queryset in minimal DB queries.
    """
    stats = queryset.aggregate(
        min_price=Min('price'),
        max_price=Max('price'),
        in_stock_count=Count('id', filter=Q(in_stock=True)),
        out_of_stock_count=Count('id', filter=Q(in_stock=False)),
        total_count=Count('id')
    )

    categories = [
        {
            'id': item['category__id'],
            'name': item['category__name'],
            'slug': item['category__slug'],
            'count': item['count']
        }
        for item in queryset.values(
            'category__id', 'category__name', 'category__slug'
        ).annotate(count=Count('id')).order_by('category__name')
        if item['category__id'] is not None
    ]

    return {
        'price_range': {
            'min': float(stats['min_price']) if stats['min_price'] is not None else None,
            'max': float(stats['max_price']) if stats['max_price'] is not None else None,
        },
        'in_stock_count': stats['in_stock_count'],
        'out_of_stock_count': stats['out_of_stock_count'],
        'total_count': stats['total_count'],
        'categories': categories,
    }


def apply_catalog_filters(queryset, params):
    """
    Applies faceted filtering (price range, in_stock, category, search, ordering) to a queryset.
    """
    # Category filter
    category_param = (params.get('category') or params.get('category_slug') or '').strip()
    if category_param:
        if category_param.isdigit():
            queryset = queryset.filter(category_id=int(category_param))
        else:
            queryset = queryset.filter(category__slug=category_param)

    # Price range filter
    min_price = params.get('min_price')
    if min_price is not None and str(min_price).strip() != '':
        try:
            queryset = queryset.filter(price__gte=float(min_price))
        except (ValueError, TypeError):
            pass

    max_price = params.get('max_price')
    if max_price is not None and str(max_price).strip() != '':
        try:
            queryset = queryset.filter(price__lte=float(max_price))
        except (ValueError, TypeError):
            pass

    # In stock filter
    in_stock = params.get('in_stock')
    if in_stock is not None and str(in_stock).strip() != '':
        in_stock_str = str(in_stock).strip().lower()
        if in_stock_str in ('true', '1', 'yes'):
            queryset = queryset.filter(in_stock=True)
        elif in_stock_str in ('false', '0', 'no'):
            queryset = queryset.filter(in_stock=False)

    # Search query handling
    search = (params.get('search') or params.get('q') or '').strip()
    if search:
        terms = [t for t in search.split() if t]
        if len(terms) > 1:
            term_filter = Q()
            for term in terms:
                term_filter &= (Q(title__icontains=term) | Q(description__icontains=term))
            queryset = queryset.filter(Q(title__icontains=search) | Q(description__icontains=search) | term_filter)
        else:
            queryset = queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))

    # Ordering
    ordering = params.get('ordering', '').strip()
    allowed_orderings = {
        'price': 'price',
        '-price': '-price',
        'created_at': 'created_at',
        '-created_at': '-created_at',
        'title': 'title',
        '-title': '-title',
        'name': 'title',
        '-name': '-title',
    }
    if ordering in allowed_orderings:
        queryset = queryset.order_by(allowed_orderings[ordering])

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
    queryset = Product.objects.select_related('category', 'created_by')
    permission_classes = [IsReviewReadOnly | SellerModifyOrReadOnly | IsAdminUserForObject | IsSellerUser]

    def get_serializer_class(self):
        if self.action in ('list', 'create'):
            return ProductSerializer
        return ProductDetailSerializer

    def get_queryset(self):
        queryset = self.queryset.all()
        if self.action == 'retrieve':
            queryset = queryset.prefetch_related(
                Prefetch('reviews', queryset=Review.objects.select_related('created_by')),
                'images'
            )
        return apply_catalog_filters(queryset, self.request.query_params)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data['facets'] = compute_facets(queryset)
            response.data['is_empty'] = (response.data.get('count') == 0)
            return response

        serializer = self.get_serializer(queryset, many=True)
        count = queryset.count()
        return Response({
            'count': count,
            'results': serializer.data,
            'is_empty': (count == 0),
            'facets': compute_facets(queryset)
        })

    @action(detail=False, methods=['get'])
    def facets(self, request):
        """
        Return facet aggregations (categories, price range, stock) for current query filters
        """
        queryset = self.get_queryset()
        return Response(compute_facets(queryset))


class CategoryViewSet(viewsets.ModelViewSet):
    lookup_field = "slug"
    queryset = Category.objects.select_related('created_by')
    permission_classes = [CategoryPermission]
    serializer_class = CategorySerializer

    def retrieve(self, request, *args, **kwargs):
        """
        Returns the products in category -> Category details with faceted filtering
        """
        category = get_object_or_404(Category.objects.select_related('created_by'), slug=kwargs.get('slug'))

        base_queryset = Product.objects.filter(category=category, is_active=True).select_related(
            'category', 'created_by'
        )

        category_facets = compute_facets(base_queryset)

        # Apply faceted filters
        query_set = apply_catalog_filters(base_queryset, request.query_params)

        paginator = PageNumberPagination()
        paginator.page_size = settings.PAGINATION_PAGE_SIZE
        paginated_queryset = paginator.paginate_queryset(query_set, request)

        category_data = CategorySerializer(category).data

        if paginated_queryset is not None:
            products = ProductSerializer(paginated_queryset, many=True, context={'request': request}).data
            count = paginator.page.paginator.count
            return Response({
                "category": category_data,
                "products": {
                    "count": count,
                    "next": paginator.get_next_link(),
                    "previous": paginator.get_previous_link(),
                    "results": products,
                    "is_empty": count == 0
                },
                "facets": category_facets
            })

        products = ProductSerializer(query_set, many=True, context={'request': request}).data
        count = query_set.count()
        return Response({
            "category": category_data,
            "products": {
                "count": count,
                "next": None,
                "previous": None,
                "results": products,
                "is_empty": count == 0
            },
            "facets": category_facets
        })

    @action(detail=True, methods=['get'])
    def facets(self, request, slug=None):
        """
        Returns faceted aggregation for this specific category
        """
        category = get_object_or_404(Category, slug=slug)
        base_queryset = Product.objects.filter(category=category, is_active=True)
        return Response(compute_facets(base_queryset))


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

