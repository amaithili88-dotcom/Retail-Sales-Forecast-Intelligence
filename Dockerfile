FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements-web.txt /app/requirements-web.txt
RUN pip install --no-cache-dir -r /app/requirements-web.txt

COPY . /app

EXPOSE 8501

CMD ["gunicorn", "-w", "2", "-k", "gthread", "-b", "0.0.0.0:8501", "wsgi:app"]
