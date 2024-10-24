FROM python:3.10-slim as base

RUN export http_proxy=http://10.230.143.15:3128 && export https_proxy=http://10.230.143.15:3128
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIPENV_VERBOSITY=-1
ENV TZ=Asia/Bishkek

WORKDIR /app

# stage for installing dependencies
FROM base as dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    gcc

RUN python3 -m venv --copies .venv
COPY Pipfile Pipfile.lock ./
RUN . .venv/bin/activate \
&& pip3 install pipenv \
&& pipenv install --deploy --skip-lock