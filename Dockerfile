FROM python:3.11-slim-buster

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY alembic alembic
COPY alembic.ini alembic.ini
COPY src/ /app/src/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000
