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
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductImage)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Review)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Specification)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Sales)
class CategoryAdmin(admin.ModelAdmin):
    pass
