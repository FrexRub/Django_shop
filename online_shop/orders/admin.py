from django.contrib import admin

from orders.models import Order, OrderInfoBasket


class OrderInline(admin.TabularInline):
    model = OrderInfoBasket
    extra = 2


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    list_display = ("id", "name_order", "delivery_type", "status")
    list_display_links = (
        "id",
        "name_order",
    )
    inlines = [
        OrderInline,
    ]

    def name_order(self, obj: Order):
        return f"id{obj.pk}_by_user_{obj.user.username}_{obj.created_at.strftime('%B %d %Y')}"
