FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# psycopg2-binary uchun runtime kutubxona
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

# root bo'lmagan foydalanuvchi
RUN useradd --create-home --uid 1000 snaber \
    && mkdir -p /app/static /app/media \
    && chown -R snaber:snaber /app
USER snaber

EXPOSE 8020

CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py createcachetable && python manage.py collectstatic --noinput && exec python -m gunicorn --workers 3 --bind 0.0.0.0:8020 --access-logfile - config.wsgi:application"]
