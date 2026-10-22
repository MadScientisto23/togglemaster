FROM python:3.11-alpine AS builder

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"


WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-alpine

RUN apk update && apk add --no-cache aws-cli
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"


RUN addgroup -S appgroup && adduser -S -u 10001 -H -G appgroup appuser

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --chown=appuser:appgroup app.py .

USER appuser

EXPOSE 8005

CMD ["gunicorn", "--bind", "0.0.0.0:8005", "--workers", "1", "--threads", "2", "app:app"]
