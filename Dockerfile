# Dockerfile pour Render (optionnel)
FROM python:3.11-slim

WORKDIR /app


COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

ENV PORT 8000

CMD gunicorn core.wsgi:application --bind 0.0.0.0:$PORT
