FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends unixodbc \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r /app/requirements.txt

COPY backend/ /app
COPY prompts/ /prompts

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py seed_dental_data && exec python manage.py runserver 0.0.0.0:8000"]
