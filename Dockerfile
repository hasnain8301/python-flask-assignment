FROM python:3.10

ARG JWT_SECRET_KEY
ARG MONGODB_URI
ARG SENTRY_DNS

ENV JWT_SECRET_KEY=${JWT_SECRET_KEY}
ENV MONGODB_URI=${MONGODB_URI}
ENV SENTRY_DNS=${SENTRY_DNS}

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

COPY . .
EXPOSE 5000

CMD ["python", "run.py"]
