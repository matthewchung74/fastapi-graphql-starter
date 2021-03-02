FROM python:3.9.2

WORKDIR /app/

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY pyproject.toml poetry.lock* /app/
COPY  ./alembic.ini /app/
COPY  ./schema.graphql /app/

RUN pip install 'poetry==1.1.4'.
RUN poetry config virtualenvs.create false
RUN poetry install --no-root

COPY ./app /app/app
ENV PYTHONPATH=/app
EXPOSE 8000 8000
