from django.contrib import admin
from orders.models import Order


class OrderAdmin(admin.ModelAdmin):
    list_display_links = (
        "created_by",
        "payment_token",
    )
    list_display = (
        "payment_token",
        "created_by",
        "status",
        "paid_amount",
        "paid",
        "cash_on_delivery",
        "delivered",
        "created_at",
    )
    list_filter = ("status", "paid", "delivered", "cash_on_delivery", "created_at")
    search_fields = ("payment_token", "first_name", "last_name", "email", "phone")


admin.site.register(Order, OrderAdmin)
