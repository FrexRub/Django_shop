from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404

from shopapp.models import (
    Product,
    Category,
)


def get_order_field(sort: str, sort_type: str) -> str:
    """
    Формирование аргумента для сортировки списка продуктов
    :param sort:
        поле сортировки
    :param sort_type:
        направление сортировки
    :return: str
        сформированный аргумент сортировки
    """

    res = "count_reviews" if sort == "reviews" else sort
    res = "-" + res if sort_type == "inc" else res

    return res


def sorted_products(request):
    min_price = request.GET.get("filter[minPrice]")
    max_price = request.GET.get("filter[maxPrice]")
    free_delivery = (
        True
        if request.GET.get("filter[freeDelivery]").capitalize() == "True"
        else False
    )
    available = (
        True if request.GET.get("filter[available]").capitalize() == "True" else False
    )
    sort = request.GET.get("sort")
    sort_type = request.GET.get("sortType")
    tags = request.GET.getlist("tags[]")

    category_id = int(request.GET.get("category"))
    limit = int(request.GET.get("limit"))

    category: Category = get_object_or_404(Category, pk=category_id)
    filters = Q()
    filters &= Q(category=category)  # фильтр по категории
    filters &= Q(price__range=(min_price, max_price))  # фильтр по цене

    # фильтр по доставке (бесплатная/платная)
    # если фильтр установлен, то сортируем - иначе выводим все товары
    if free_delivery:
        filters &= Q(
            freeDelivery=free_delivery
        )

    if available:
        filters &= Q(count__gt=0)  # фильтр по наличию товара

    if tags:
        filters &= Q(tags__in=tags)  # фильтр по тэгам

    # установка поля таблицы для cортировки по (популярности, цене, отзывам, новизне)
    sorted = get_order_field(sort, sort_type)

    queryset: Product = (
        Product.objects.filter(filters)
        .annotate(rating=Avg("reviews__rate"))
        .annotate(count_reviews=Count("reviews__id"))
        .select_related("category")
        .prefetch_related(
            "tags", "images", "specifications", "reviews", "reviews__author"
        )
        .order_by(sorted)[:limit]
    )
    return queryset
