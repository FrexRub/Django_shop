import logging

from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from orders.models import Order, OrderInfoBasket

log = logging.getLogger(__name__)


@shared_task
def send_email_about_order_created(order_id: int):
    """
    Задача для отправки уведомления по электронной почте при успешном создании заказа.
    """
    try:
        order = (
            Order.objects.filter(pk=order_id)
            .select_related("user")
            .first()
        )
        basket = OrderInfoBasket.objects.filter(order=order).select_related("product")

        subject = "Order nr. {}".format(order_id)

        message = render_to_string(
            "orders/order_email_send.html",
            {
                "username": order.user.first_name,
                "order_id": order_id,
                "total_cost": order.total_cost,
                "basket": basket,
            },
        )

        mail_sent = send_mail(subject, message, "admin@myshop.com", [order.user.email])
        return mail_sent
    except Order.DoesNotExist as exp:
        log.exception("Order not find: %s" % exp)
