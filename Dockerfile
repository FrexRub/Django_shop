FROM python:3.11

ENV PYTHONBUFFERED=1

RUN mkdir /app && mkdir /app/docker && mkdir /app/frontend

WORKDIR /app

RUN pip install --upgrade pip "poetry==1.8.4"

RUN poetry config virtualenvs.create false --local
COPY pyproject.toml poetry.lock ./
RUN poetry install

COPY online_shop .
# COPY . .
COPY diploma-frontend/frontend /app/frontend
COPY docker /app/docker

RUN chmod a+x docker/*.sh     # разрешение на запуск скриптов из каталога docker

CMD ["gunicorn", "online_shop.wsgi:application", "--bind", "0.0.0.0:8000"]