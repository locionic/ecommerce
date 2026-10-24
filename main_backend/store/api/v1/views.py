import difflib
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers, vary_on_cookie
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count

from rest_framework import viewsets, generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from store.api.v1.permissions import (
    CreatorModifyOrReadOnly,
    IsAdminUserForObject,
    IsSellerUser,
    SellerModifyOrReadOnly,
    IsReviewReadOnly,
    CategoryPermission,
    CreateOrCreatorModify,
)
from store.api.v1.serializers import (
    ProductSerializer,
    ProductDetailSerializer,
    AlbumSerializer,
    ReviewSerializer,
    CategorySerializer,
)
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
    queryset = (
        Product.objects.select_related("category", "created_by")
        .prefetch_related("images", "reviews", "reviews__created_by")
        .all()
    )
    permission_classes = [
        IsReviewReadOnly | SellerModifyOrReadOnly | IsAdminUserForObject | IsSellerUser
    ]

    def get_serializer_class(self):
        if self.action in ("list", "create"):
            return ProductSerializer
        return ProductDetailSerializer

    def get_queryset(self):
        queryset = self.queryset

        # 1. Search Query Handling (supports 'search' and 'q', handles multi-word and whitespace)
        search = self.request.query_params.get("search") or self.request.query_params.get("q")
        if search:
            search_text = search.strip()
            if search_text:
                search_filter = (
                    Q(title__icontains=search_text)
                    | Q(description__icontains=search_text)
                    | Q(category__name__icontains=search_text)
                    | Q(category__slug__icontains=search_text)
                )
                words = [w for w in search_text.split() if len(w) > 1]
                if len(words) > 1:
                    multi_word_filter = Q()
                    for word in words:
                        multi_word_filter &= (
                            Q(title__icontains=word)
                            | Q(description__icontains=word)
                            | Q(category__name__icontains=word)
                        )
                    search_filter |= multi_word_filter

                queryset = queryset.filter(search_filter)

        # 2. Multi-Category Filtering in Store Views
        # Supports: ?category=cat1,cat2, ?category=cat1&category=cat2, ?categories=cat1,cat2,
        # and category IDs: ?category_id=1,2
        raw_categories = []
        for key in [
            "category",
            "categories",
            "category_slug",
            "category_slugs",
            "category_id",
            "category_ids",
        ]:
            values = self.request.query_params.getlist(key)
            for val in values:
                if val:
                    for item in str(val).split(","):
                        item = item.strip()
                        if item:
                            raw_categories.append(item)

        if raw_categories:
            id_filters = [int(cat) for cat in raw_categories if cat.isdigit()]
            slug_or_name_filters = [cat for cat in raw_categories if not cat.isdigit()]

            cat_query = Q()
            if id_filters:
                cat_query |= Q(category__id__in=id_filters)
            if slug_or_name_filters:
                for s in slug_or_name_filters:
                    cat_query |= (
                        Q(category__slug__iexact=s)
                        | Q(category__name__iexact=s)
                        | Q(category__slug__in=slug_or_name_filters)
                        | Q(category__name__in=slug_or_name_filters)
                    )

            queryset = queryset.filter(cat_query)

        return queryset

    @staticmethod
    def get_category_aggregations(queryset):
        """
        Aggregate category filter facets with product counts for the current queryset.
        """
        category_counts = (
            queryset.values("category__id", "category__name", "category__slug")
            .annotate(count=Count("id"))
            .order_by("-count", "category__name")
        )
        return [
            {
                "id": row["category__id"],
                "name": row["category__name"],
                "slug": row["category__slug"],
                "count": row["count"],
            }
            for row in category_counts
            if row["category__id"] is not None
        ]

    @staticmethod
    def get_suggested_terms(search_text):
        """
        Suggest terms based on catalog categories, product titles, and keywords.
        """
        candidates = set()
        for cat in Category.objects.all():
            candidates.add(cat.name)
            for w in cat.name.split():
                if len(w) > 2:
                    candidates.add(w)

        for p in Product.objects.filter(is_active=True):
            candidates.add(p.title)
            for w in p.title.split():
                if len(w) > 2:
                    candidates.add(w)

        suggestions = []
        if search_text:
            # 1. Fuzzy match against candidates
            close_matches = difflib.get_close_matches(
                search_text, candidates, n=5, cutoff=0.3
            )
            for m in close_matches:
                if m not in suggestions:
                    suggestions.append(m)

            # 2. Check individual words if multi-word
            for word in search_text.split():
                word_matches = difflib.get_close_matches(
                    word, candidates, n=3, cutoff=0.4
                )
                for m in word_matches:
                    if m not in suggestions:
                        suggestions.append(m)

            # 3. Substring matching
            lower_search = search_text.lower()
            for cand in candidates:
                if lower_search in cand.lower() or cand.lower() in lower_search:
                    if cand not in suggestions:
                        suggestions.append(cand)

        # 4. Fallback if fewer suggestions: popular categories and products
        if len(suggestions) < 3:
            for cat in Category.objects.annotate(p_count=Count("product")).order_by("-p_count")[:5]:
                if cat.name not in suggestions:
                    suggestions.append(cat.name)

        if len(suggestions) < 5:
            for p in Product.objects.filter(is_active=True).order_by("-created_at")[:5]:
                if p.title not in suggestions:
                    suggestions.append(p.title)

        return suggestions[:5]

    @staticmethod
    def get_suggested_categories(search_text=None):
        """
        Suggest categories based on search text or top categories in catalog.
        """
        suggested = []
        seen_ids = set()

        if search_text:
            matching_cats = Category.objects.filter(
                Q(name__icontains=search_text) | Q(slug__icontains=search_text)
            ).annotate(count=Count("product", filter=Q(product__is_active=True)))

            for cat in matching_cats:
                if cat.id not in seen_ids:
                    seen_ids.add(cat.id)
                    suggested.append({
                        "id": cat.id,
                        "name": cat.name,
                        "slug": cat.slug,
                        "count": cat.count,
                    })

            # Fuzzy match category names
            all_cats = list(
                Category.objects.annotate(
                    count=Count("product", filter=Q(product__is_active=True))
                )
            )
            cat_names = [c.name for c in all_cats]
            close_names = difflib.get_close_matches(search_text, cat_names, n=3, cutoff=0.3)
            for name in close_names:
                for cat in all_cats:
                    if cat.name == name and cat.id not in seen_ids:
                        seen_ids.add(cat.id)
                        suggested.append({
                            "id": cat.id,
                            "name": cat.name,
                            "slug": cat.slug,
                            "count": cat.count,
                        })

        top_cats = (
            Category.objects.annotate(count=Count("product", filter=Q(product__is_active=True)))
            .order_by("-count", "name")
        )
        for cat in top_cats:
            if cat.id not in seen_ids:
                seen_ids.add(cat.id)
                suggested.append({
                    "id": cat.id,
                    "name": cat.name,
                    "slug": cat.slug,
                    "count": cat.count,
                })
            if len(suggested) >= 5:
                break

        return suggested[:5]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        search = self.request.query_params.get("search") or self.request.query_params.get("q")
        search_text = search.strip() if search else ""

        aggregations = self.get_category_aggregations(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={"request": request})
            response = self.get_paginated_response(serializer.data)
            total_count = response.data.get("count", len(serializer.data))

            response.data["category_aggregations"] = aggregations
            if total_count == 0:
                suggested_terms = self.get_suggested_terms(search_text)
                suggested_categories = self.get_suggested_categories(search_text)
                response.data["suggested_terms"] = suggested_terms
                response.data["suggested_categories"] = suggested_categories
                response.data["suggestions"] = {
                    "terms": suggested_terms,
                    "categories": suggested_categories,
                }
            else:
                response.data["suggested_terms"] = []
                response.data["suggested_categories"] = []
                response.data["suggestions"] = {
                    "terms": [],
                    "categories": [],
                }
            return response

        serializer = self.get_serializer(queryset, many=True, context={"request": request})
        total_count = len(serializer.data)
        data = {
            "count": total_count,
            "results": serializer.data,
            "category_aggregations": aggregations,
        }
        if total_count == 0:
            suggested_terms = self.get_suggested_terms(search_text)
            suggested_categories = self.get_suggested_categories(search_text)
            data["suggested_terms"] = suggested_terms
            data["suggested_categories"] = suggested_categories
            data["suggestions"] = {
                "terms": suggested_terms,
                "categories": suggested_categories,
            }
        else:
            data["suggested_terms"] = []
            data["suggested_categories"] = []
            data["suggestions"] = {
                "terms": [],
                "categories": [],
            }
        return Response(data)


class CategoryViewSet(viewsets.ModelViewSet):
    lookup_field = "slug"
    queryset = Category.objects.select_related("created_by").prefetch_related(
        "product", "product__category", "product__created_by"
    ).all()
    permission_classes = [CategoryPermission]
    serializer_class = CategorySerializer

    def retrieve(self, request, *args, **kwargs):
        """
        Returns the products in category -> Category details
        """
        category = get_object_or_404(
            Category.objects.select_related("created_by"), slug=kwargs.get("slug")
        )

        products = category.product.filter(
            is_active=True, in_stock=True
        ).select_related("category", "created_by")

        paginator = PageNumberPagination()
        paginator.page_size = settings.PAGINATION_PAGE_SIZE
        paginated_products = paginator.paginate_queryset(products, request)

        category_data = CategorySerializer(category).data
        products_data = ProductSerializer(
            paginated_products, many=True, context={"request": request}
        ).data

        return Response({
            "category": category_data,
            "products": {
                "count": paginator.page.paginator.count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "results": products_data,
            },
        })


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related("created_by", "content_object").all()
    permission_classes = [CreateOrCreatorModify]
    serializer_class = ReviewSerializer
    content_type_pk = ContentType.objects.get(app_label="store", model="product").pk

    def create(self, request, *args, **kwargs):
        custom_data = request.data
        custom_data["content_type"] = self.content_type_pk
        serializer = self.get_serializer(data=custom_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        if not self.request.user.is_anonymous:
            serializer.save(created_by=self.request.user)


class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.select_related("created_by").all()
    permission_classes = [CreatorModifyOrReadOnly | IsAdminUserForObject]
    serializer_class = AlbumSerializer
