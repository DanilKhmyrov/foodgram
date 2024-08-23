FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app

RUN pip install gunicorn==20.1.0

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram.wsgi"]