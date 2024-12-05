import logging

from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from orders.models import Order


log = logging.getLogger(__name__)


@shared_task
def send_email_about_order_created(user_name: str, order_id: int):
    """
    Задача для отправки уведомления по электронной почте при успешном создании заказа.
    """
    try:
        order = (
            Order.objects.filter(pk=order_id)
            .select_related("user")
            .prefetch_related("basket")
            .first()
        )

        subject = "Order nr. {}".format(order_id)
        # message = "Dear {},\n\nYou have successfully placed an order.\
        #             Your order id is {}.".format(
        #     user_name, order_id
        # )

        message = render_to_string(
            "orders/order_email_send.html",
            {
                "user": order.user,
                "order_id": order_id,
            },
        )

        mail_sent = send_mail(subject, message, "admin@myshop.com", [order.user.email])
        return mail_sent
    except Order.DoesNotExist as exp:
        log.exception("Order not find: %s" % exp)
