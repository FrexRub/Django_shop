from django.contrib import admin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import path

from orders.models import Order, OrderInfoBasket
from orders.forms import CSVImportForm
from orders.admin_mixins import ExportAsCSVMixin


class OrderInline(admin.TabularInline):
    model = OrderInfoBasket
    extra = 2


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    # change_list_template = "orders/order_changelist.html"
    actions = [
        "export_as_csv",
    ]
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

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportForm()
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context, status=400)

        # save_csv_products(
        #     file=form.files["csv_file"].file,
        #     encoding=request.encoding,
        # )

        self.message_user(request, "Data from CSV was imported")
        return redirect("..")

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path("import_orders_csv/", self.import_csv, name="import_orders_csv"),
        ]
        return new_urls + urls
