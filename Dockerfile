FROM python:3.11-slim-buster

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

COPY alembic alembic
COPY alembic.ini alembic.ini
COPY src/ /app/src/

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000"]
