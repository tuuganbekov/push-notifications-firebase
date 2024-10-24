FROM python:3.11 as python-base

ENV HTTP_PROXY=http://10.230.143.15:3128
ENV HTTPS_PROXY=http://10.230.143.15:3128
ENV PYTHONDONTWRITEBYTECODE = 1 \
    PYTHONUNBUFFERED = 1


WORKDIR /push_notifications
COPY poetry.lock pyproject.toml /push_notifications/

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-root

COPY . /push_notifications/