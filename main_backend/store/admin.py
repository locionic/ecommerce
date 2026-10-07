from django.contrib import admin
from store.models import Product, Album, Review, Category, Wishlist

admin.site.register(Category)


class AlbumAdmin(admin.ModelAdmin):
    list_display_links = ("id",)
    list_display = (
        "id",
        "image",
        "created_by",
        "content_type",
        "object_id",
        "content_object",
    )


admin.site.register(Album, AlbumAdmin)
admin.site.register(Review)


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display_links = ("id", "title",)
    list_display = (
        "id",
        "title",
        "created_by",
        "thumbnail"
    )


admin.site.register(Product, ProductAdmin)


class WishlistAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "product__title")


admin.site.register(Wishlist, WishlistAdmin)
