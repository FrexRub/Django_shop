FROM python:3.11

RUN mkdir /app && mkdir /app/docker && mkdir /app/frontend

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get -y dist-upgrade
RUN apt install netcat-traditional
RUN pip install --upgrade pip "poetry==1.8.4"

RUN poetry config virtualenvs.create false --local
COPY pyproject.toml poetry.lock ./
RUN poetry install

COPY online_shop .
COPY diploma-frontend/frontend /app/frontend
COPY docker /app/docker

RUN chmod a+x docker/*.sh     # разрешение на запуск скриптов из каталога docker

ENTRYPOINT ["docker/entrypoint.sh"]