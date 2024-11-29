import re
import logging

from rest_framework.request import Request
from rest_framework import status

log = logging.getLogger(__name__)


def validate_score(score: int) -> bool:
    return bool((score % 2 == 0) and (len(str(score)) == 8))


def checking_payments(request: Request):
    response = dict()
    if not re.search(r"^[а-яА-ЯёЁa-zA-Z]+ ?[а-яА-ЯёЁa-zA-Z]+$", request.data["name"]):
        log.info("Имя указано не верно")
        response["massage"] = "Имя указано не верно"
        response["status"] = status.HTTP_400_BAD_REQUEST
        return response

    if not re.search(r"^\d{8}$", request.data["number"]):
        log.info("Счёт указано не верно")
        response["massage"] = "Счёт указано не верно"
        response["status"] = status.HTTP_400_BAD_REQUEST
        return response

    if not re.search(r"^\d{2}$", request.data["year"]):
        log.info("Год указан не верно")
        response["massage"] = "Год указан не верно"
        response["status"] = status.HTTP_400_BAD_REQUEST
        return response

    if not (re.search(r"^\d{2}$", request.data["month"])
            and (int(request.data["month"]) > 0 and int(request.data["month"]) < 13)):
        log.info("Месяц указан не верно")
        response["massage"] = "Месяц указан не верно"
        response["status"] = status.HTTP_400_BAD_REQUEST
        return response

    if not re.search(r"^\d{3}$", request.data["code"]):
        log.info("Код указан не верно")
        response["massage"] = "Код указан не верно"
        response["status"] = status.HTTP_400_BAD_REQUEST
        return response

    response["massage"] = "Данные указаны верно"
    response["status"] = status.HTTP_200_OK
    log.info("Данные указаны верно")

    return response


