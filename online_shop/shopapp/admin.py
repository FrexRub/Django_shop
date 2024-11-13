from django.contrib import admin

from .models import (
    Tag,
    Category,
    Product,
    ProductImage,
    Review,
    Specification,
    Sales,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "price",
        "count",
    )
    list_display_links = ("title",)
    search_fields = "title", "price"


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    pass


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    pass


@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    pass


@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    pass
